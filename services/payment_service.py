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
from sqlalchemy.orm import Session

from models import Payment, Subscription, Invoice, Plan, User
from services.email_service import EmailService

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_your_api_key")

class PaymentService:
    """Service to handle payment processing and integration with payment gateways"""
    
    @staticmethod
    def handle_payment_succeeded(db: Session, payment_intent: Dict):
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
    def handle_payment_failed(db: Session, payment_intent: Dict):
        """Handle failed payment event"""
        transaction_id = payment_intent["id"]

        # Find the payment record in the database
        payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()

        if payment:
            payment.status = "failed"
            error_message = payment_intent.get("last_payment_error", {}).get("message", "Unknown error")
            payment.error_message = error_message
            db.commit()

        # Send payment failed email
        PaymentService._send_payment_failed_email(payment, db)

        return payment
    
    @staticmethod
    def handle_invoice_paid(db: Session, invoice: Dict):
        """Handle invoice paid event"""
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
                    amount=invoice["amount_paid"] / 100,
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
    def handle_invoice_payment_failed(db: Session, invoice: Dict):
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
    def handle_subscription_created(db: Session, subscription: Dict, gateway: str = "stripe"):
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
    def handle_subscription_updated(db: Session, subscription: Dict):
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
    def handle_subscription_deleted(db: Session, subscription: Dict):
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
    def _handle_payment_succeeded(db: Session, gateway: str, payment_data: Dict):
        """Handle successful payment event"""
        payment_id = payment_data.get('id') or payment_data.get('payment_intent')
        status = 'succeeded'

        # Update payment status in database
        PaymentService._update_payment_status_in_db(db, payment_id, status)

        print(f"Payment succeeded via {gateway}: {payment_id}")

    @staticmethod
    def _handle_payment_failed(db: Session, gateway: str, payment_data: Dict):
        """Handle failed payment event"""
        payment_id = payment_data.get('id') or payment_data.get('payment_intent')
        error_message = payment_data.get('last_payment_error', {}).get('message', 'Unknown error')
        status = 'failed'

        # Update payment status and record error
        PaymentService._update_payment_status_in_db(db, payment_id, status, error_message)

        print(f"Payment failed via {gateway}: {payment_id} - {error_message}")

    @staticmethod
    def _handle_subscription_created(db: Session, gateway: str, subscription_data: Dict):
        """Handle subscription created event"""
        subscription_id = subscription_data.get('id')
        status = 'active'

        # Update subscription status in database
        PaymentService._update_subscription_status_in_db(db, subscription_id, status)

        print(f"Subscription created via {gateway}: {subscription_id}")

    @staticmethod
    def _handle_subscription_updated(db: Session, gateway: str, subscription_data: Dict):
        """Handle subscription updated event"""
        subscription_id = subscription_data.get('id')
        status = subscription_data.get('status')

        # Update subscription status in database
        PaymentService._update_subscription_status_in_db(db, subscription_id, status)

        print(f"Subscription updated via {gateway}: {subscription_id} - Status: {status}")

    @staticmethod
    def _handle_subscription_deleted(db: Session, gateway: str, subscription_data: Dict):
        """Handle subscription deleted event"""
        subscription_id = subscription_data.get('id')
        status = 'cancelled'

        # Update subscription status in database
        PaymentService._update_subscription_status_in_db(db, subscription_id, status)

        print(f"Subscription deleted via {gateway}: {subscription_id}")

    @staticmethod
    def _update_payment_status_in_db(db: Session, payment_id: str, status: str, error_message: str = None):
        """Update payment status in database"""
        payment = db.query(Payment).filter(Payment.transaction_id == payment_id).first()
        if payment:
            payment.status = status
            if error_message:
                payment.error_message = error_message
            db.commit()
            return True
        return False

    @staticmethod
    def _update_subscription_status_in_db(db: Session, subscription_id: str, status: str):
        """Update subscription status in database"""
        subscription = db.query(Subscription).filter(Subscription.stripe_subscription_id == subscription_id).first()
        if subscription:
            subscription.status = status
            db.commit()
            return True
        return False
    
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