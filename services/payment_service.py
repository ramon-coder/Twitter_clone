"""
Payment Service for Subscription and Recurring Payments Management System

This module provides payment gateway integration and processing logic.
It handles Stripe webhook events, payment status updates, and subscription
management related to payments.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import stripe

from models import Payment, Subscription, Invoice, Plan, User
from services.email_service import EmailService

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_your_api_key")

class PaymentService:
    """Service to handle payment processing and integration with payment gateways"""
    
    @staticmethod
    def handle_payment_succeeded(db, payment_intent: Dict):
        """Handle successful payment event"""
        transaction_id = payment_intent["id"]
        subscription_id = payment_intent["metadata"].get("subscription_id")
        
        # Find the payment record in the database
        payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
        
        if not payment:
            # Create a new payment record if it doesn't exist
            user_id = int(payment_intent["metadata"].get("user_id"))
            payment = Payment(
                user_id=user_id,
                subscription_id=int(subscription_id) if subscription_id else None,
                amount=payment_intent["amount"] / 100,  # Convert from cents to dollars
                currency=payment_intent["currency"],
                status="succeeded",
                payment_method="stripe",
                transaction_id=transaction_id
            )
            db.add(payment)
        else:
            # Update existing payment record
            payment.status = "succeeded"
        
        # If this is a subscription payment, update the subscription status
        if subscription_id:
            subscription = db.query(Subscription).filter(Subscription.id == int(subscription_id)).first()
            if subscription and subscription.status != "active":
                subscription.status = "active"
                # If auto-renew is enabled, calculate new end date
                if subscription.auto_renew:
                    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
                    if plan:
                        subscription.end_date = datetime.utcnow() + timedelta(days=plan.duration)
        
        db.commit()
        
        # Send payment confirmation email
        PaymentService._send_payment_confirmation(payment, db)
        
        return payment
    
    @staticmethod
    def handle_payment_failed(db, payment_intent: Dict):
        """Handle failed payment event"""
        transaction_id = payment_intent["id"]
        
        # Find the payment record in the database
        payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
        
        if payment:
            payment.status = "failed"
            error_message = payment_intent.get("last_payment_error", {}).get("message", "Unknown error")
            payment.error_message = error_message  # Assuming you have an error_message column
            db.commit()
        
        # Send payment failed email
        PaymentService._send_payment_failed_email(payment, db)
        
        return payment
    
    @staticmethod
    def handle_invoice_paid(db, invoice: Dict):
        """Handle invoice paid event"""
        # Create invoice record in the database
        invoice_number = invoice["number"]
        customer_email = invoice["customer_email"]
        
        user = db.query(User).filter(User.email == customer_email).first()
        
        if user:
            subscription_id = None
            if invoice.get("subscription"):
                # Find subscription by Stripe subscription ID
                subscription = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == invoice["subscription"]
                ).first()
                if subscription:
                    subscription_id = subscription.id
            
            # Check if invoice already exists
            existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
            
            if not existing_invoice:
                new_invoice = Invoice(
                    user_id=user.id,
                    subscription_id=subscription_id,
                    amount=invoice["amount_paid"] / 100,  # Convert from cents to dollars
                    currency=invoice["currency"],
                    due_date=datetime.fromtimestamp(invoice["due_date"]),
                    status="paid",
                    invoice_number=invoice_number
                )
                db.add(new_invoice)
                db.commit()
        
        # Send invoice email
        PaymentService._send_invoice_email(invoice, customer_email)
        
        return invoice
    
    @staticmethod
    def handle_invoice_payment_failed(db, invoice: Dict):
        """Handle invoice payment failed event"""
        invoice_number = invoice["number"]
        customer_email = invoice["customer_email"]
        
        # Find the invoice in the database
        existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
        
        if existing_invoice:
            existing_invoice.status = "overdue"
            db.commit()
        
        # Send payment failed email
        PaymentService._send_invoice_payment_failed_email(invoice, customer_email)
        
        return invoice
    
    @staticmethod
    def handle_subscription_created(db, subscription: Dict):
        """Handle subscription created event"""
        stripe_subscription_id = subscription["id"]
        customer_email = subscription["customer_email"]
        
        user = db.query(User).filter(User.email == customer_email).first()
        
        if user:
            # Find the plan associated with this subscription
            plan = PaymentService._get_plan_from_stripe_product(subscription["items"]["data"][0]["price"]["product"])
            
            if plan:
                # Create or update subscription record in the database
                existing_subscription = db.query(Subscription).filter(
                    Subscription.stripe_subscription_id == stripe_subscription_id
                ).first()
                
                start_date = datetime.fromtimestamp(subscription["current_period_start"])
                end_date = datetime.fromtimestamp(subscription["current_period_end"])
                
                if not existing_subscription:
                    new_subscription = Subscription(
                        user_id=user.id,
                        plan_id=plan.id,
                        start_date=start_date,
                        end_date=end_date,
                        status="active",
                        auto_renew=True,
                        stripe_subscription_id=stripe_subscription_id
                    )
                    db.add(new_subscription)
                else:
                    existing_subscription.status = "active"
                    existing_subscription.start_date = start_date
                    existing_subscription.end_date = end_date
                
                db.commit()
        
        return subscription
    
    @staticmethod
    def handle_subscription_updated(db, subscription: Dict):
        """Handle subscription updated event"""
        stripe_subscription_id = subscription["id"]
        
        existing_subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if existing_subscription:
            existing_subscription.status = subscription["status"]
            if subscription.get("current_period_start"):
                existing_subscription.start_date = datetime.fromtimestamp(subscription["current_period_start"])
            if subscription.get("current_period_end"):
                existing_subscription.end_date = datetime.fromtimestamp(subscription["current_period_end"])
            
            db.commit()
        
        return subscription
    
    @staticmethod
    def handle_subscription_deleted(db, subscription: Dict):
        """Handle subscription deleted event"""
        stripe_subscription_id = subscription["id"]
        
        existing_subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        ).first()
        
        if existing_subscription:
            existing_subscription.status = "cancelled"
            existing_subscription.auto_renew = False
            db.commit()
        
        return subscription
    
    @staticmethod
    def _get_plan_from_stripe_product(product_id: str) -> Optional[Plan]:
        """Get a plan from the database using Stripe product ID"""
        # In a real implementation, you would map Stripe product IDs to your plans
        # This could be done by adding a stripe_product_id column to the plans table
        # For now, we'll return the first active plan as a placeholder
        from sqlalchemy.orm import Session
        from main import get_db
        
        db = next(get_db())
        try:
            # This is a placeholder implementation
            # In production, you should map Stripe product IDs to your plans
            plan = db.query(Plan).filter(Plan.is_active == True).first()
            return plan
        finally:
            db.close()
    
    @staticmethod
    def _send_payment_confirmation(payment: Payment, db):
        """Send payment confirmation email to user"""
        user = db.query(User).filter(User.id == payment.user_id).first()
        
        if user:
            subject = "Payment Confirmation"
            body = f"""
Hello {user.full_name},

Your payment of ${payment.amount} has been successfully processed.

Payment Details:
- Payment ID: {payment.id}
- Amount: ${payment.amount}
- Date: {payment.created_at}
- Status: {payment.status}

Thank you for your subscription!
            """
            
            EmailService.send_email(user.email, subject, body)
    
    @staticmethod
    def _send_payment_failed_email(payment: Payment, db):
        """Send payment failed email to user"""
        user = db.query(User).filter(User.id == payment.user_id).first()
        
        if user:
            subject = "Payment Failed"
            body = f"""
Hello {user.full_name},

We were unable to process your payment of ${payment.amount}.

Payment Details:
- Payment ID: {payment.id}
- Amount: ${payment.amount}
- Date: {payment.created_at}
- Status: {payment.status}

Please update your payment information to avoid service interruption.

Thank you.
            """
            
            EmailService.send_email(user.email, subject, body)
    
    @staticmethod
    def _send_invoice_email(invoice: Dict, customer_email: str):
        """Send invoice email to user"""
        subject = "Invoice Paid"
        body = f"""
Hello,

Your invoice #{invoice["number"]} has been paid successfully.

Invoice Details:
- Invoice Number: {invoice["number"]}
- Amount: ${invoice["amount_paid"] / 100}
- Date: {datetime.fromtimestamp(invoice["created"])}
- Status: Paid

Thank you for your subscription!
        """
        
        EmailService.send_email(customer_email, subject, body)
    
    @staticmethod
    def _send_invoice_payment_failed_email(invoice: Dict, customer_email: str):
        """Send invoice payment failed email to user"""
        subject = "Invoice Payment Failed"
        body = f"""
Hello,

We were unable to process payment for your invoice #{invoice["number"]}.

Invoice Details:
- Invoice Number: {invoice["number"]}
- Amount: ${invoice["amount_due"] / 100}
- Due Date: {datetime.fromtimestamp(invoice["due_date"])}
- Status: Payment Failed

Please update your payment information to avoid service interruption.

Thank you.
        """
        
        EmailService.send_email(customer_email, subject, body)