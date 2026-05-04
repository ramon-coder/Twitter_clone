"""
Payments Router for Subscription and Recurring Payments Management System

This module provides endpoints for managing payments and integrating with
payment gateways like Stripe. It includes operations for creating payments,
processing webhooks, and managing payment statuses.
"""

import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

import stripe

from main import get_db, get_current_active_user
from models import Payment, Subscription, User
from services.payment_service import PaymentService

router = APIRouter()

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_your_api_key")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "your_webhook_secret")

@router.get("/", response_model=List[dict])
async def get_payments(
    user_id: Optional[int] = None,
    subscription_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all payments.
    
    Args:
        user_id: Optional user ID to filter payments by user
        subscription_id: Optional subscription ID to filter payments by subscription
        status: Optional status to filter payments by status
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        List of payments
    """
    # Only admin can list all payments without user filter
    if user_id is None and not current_user.is_admin:
        user_id = current_user.id
    
    # Build query
    query = db.query(Payment)
    
    if user_id:
        query = query.filter(Payment.user_id == user_id)
    
    if subscription_id:
        query = query.filter(Payment.subscription_id == subscription_id)
    
    if status:
        query = query.filter(Payment.status == status)
    
    payments = query.all()
    
    return [
        {
            "id": payment.id,
            "user_id": payment.user_id,
            "subscription_id": payment.subscription_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "payment_method": payment.payment_method,
            "transaction_id": payment.transaction_id,
            "created_at": payment.created_at.isoformat()
        }
        for payment in payments
    ]

@router.get("/{payment_id}", response_model=dict)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific payment.
    
    Args:
        payment_id: ID of the payment to retrieve
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Payment details
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Only admin or payment owner can view details
    if not current_user.is_admin and payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )
    
    return {
        "id": payment.id,
        "user_id": payment.user_id,
        "subscription_id": payment.subscription_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status,
        "payment_method": payment.payment_method,
        "transaction_id": payment.transaction_id,
        "created_at": payment.created_at.isoformat()
    }

@router.post("/create-payment-intent", response_model=dict)
async def create_payment_intent(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a payment intent for a subscription.
    
    Args:
        subscription_id: ID of the subscription to create payment for
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Payment intent details
    """
    # Get the subscription and its plan
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Check if user owns the subscription
    if not current_user.is_admin and subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create payment for this subscription"
        )
    
    # Get the plan details to calculate payment amount
    from models import Plan
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    try:
        # Create Stripe payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(plan.price * 100),  # Convert to cents
            currency="usd",
            description=f"Payment for subscription to {plan.name}",
            metadata={
                "subscription_id": str(subscription_id),
                "user_id": str(subscription.user_id)
            }
        )
        
        # Create payment record in database
        new_payment = Payment(
            user_id=subscription.user_id,
            subscription_id=subscription_id,
            amount=plan.price,
            currency="USD",
            status="pending",
            payment_method="stripe",
            transaction_id=payment_intent.id
        )
        
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        
        return {
            "message": "Payment intent created successfully",
            "payment": {
                "id": new_payment.id,
                "user_id": new_payment.user_id,
                "subscription_id": new_payment.subscription_id,
                "amount": new_payment.amount,
                "currency": new_payment.currency,
                "status": new_payment.status,
                "payment_method": new_payment.payment_method,
                "transaction_id": new_payment.transaction_id,
                "created_at": new_payment.created_at.isoformat()
            },
            "client_secret": payment_intent.client_secret
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment intent: {str(e)}"
        )

@router.post("/webhook", response_model=dict)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    Args:
        request: Request object containing webhook data
        db: Database session
    
    Returns:
        Success message
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payload: {str(e)}"
        )
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid signature: {str(e)}"
        )
    
    # Handle the event
    event_type = event["type"]
    
    if event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        PaymentService.handle_payment_succeeded(db, payment_intent)
    
    elif event_type == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        PaymentService.handle_payment_failed(db, payment_intent)
    
    elif event_type == "invoice.paid":
        invoice = event["data"]["object"]
        PaymentService.handle_invoice_paid(db, invoice)
    
    elif event_type == "invoice.payment_failed":
        invoice = event["data"]["object"]
        PaymentService.handle_invoice_payment_failed(db, invoice)
    
    elif event_type == "customer.subscription.created":
        subscription = event["data"]["object"]
        PaymentService.handle_subscription_created(db, subscription)
    
    elif event_type == "customer.subscription.updated":
        subscription = event["data"]["object"]
        PaymentService.handle_subscription_updated(db, subscription)
    
    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        PaymentService.handle_subscription_deleted(db, subscription)
    
    return {"message": "Webhook event processed successfully"}

@router.put("/{payment_id}/refund", response_model=dict)
async def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Refund a payment.
    
    Args:
        payment_id: ID of the payment to refund
        db: Database session
        current_user: Current authenticated user
    
    Returns:
        Success message
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Only admin or payment owner can refund payment
    if not current_user.is_admin and payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to refund this payment"
        )
    
    if payment.status != "succeeded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment must be succeeded to be refunded"
        )
    
    try:
        # Create refund in Stripe
        refund = stripe.Refund.create(
            payment_intent=payment.transaction_id
        )
        
        # Update payment status
        payment.status = "refunded"
        db.commit()
        db.refresh(payment)
        
        return {
            "message": "Payment refunded successfully",
            "payment": {
                "id": payment.id,
                "user_id": payment.user_id,
                "subscription_id": payment.subscription_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status,
                "payment_method": payment.payment_method,
                "transaction_id": payment.transaction_id,
                "created_at": payment.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refund payment: {str(e)}"
        )