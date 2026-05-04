"""
Webhooks Router for Subscription and Recurring Payments Management System

This module provides endpoints to handle webhook events from payment gateways
such as Stripe, PayPal, and Mercado Pago. It processes events related to:
- Payment status updates
- Subscription changes
- Customer management
- Invoicing

Each webhook handler validates the incoming request, processes the event,
and updates the system state accordingly.
"""

import hashlib
import hmac
import json
from typing import Dict, Optional
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from main import get_db
from models import Payment, Subscription, Invoice, User
from services.payment_service import PaymentService
from services.email_service import EmailService

router = APIRouter()

# Webhook configuration - Replace with your actual values
WEBHOOK_SECRETS = {
    'stripe': 'YOUR_STRIPE_WEBHOOK_SECRET',
    'paypal': 'YOUR_PAYPAL_WEBHOOK_SECRET',
    'mercado_pago': 'YOUR_MERCADO_PAGO_WEBHOOK_SECRET'
}


class WebhookEvent(BaseModel):
    """Base model for webhook events"""
    id: str
    type: str
    timestamp: datetime
    data: Dict


# Stripe Webhook Handler
@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('Stripe-Signature')
        secret = WEBHOOK_SECRETS['stripe']

        # Validate Stripe signature
        if not _validate_stripe_signature(payload, sig_header, secret):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )

        # Parse event
        event = json.loads(payload)

        # Process event based on type
        event_type = event.get('type', '')
        event_data = event.get('data', {}).get('object', {})

        if event_type == 'payment_intent.succeeded':
            PaymentService.handle_payment_succeeded(db, event_data)
        elif event_type == 'payment_intent.payment_failed':
            PaymentService.handle_payment_failed(db, event_data)
        elif event_type == 'customer.subscription.created':
            PaymentService.handle_subscription_created(db, event_data)
        elif event_type == 'customer.subscription.updated':
            PaymentService.handle_subscription_updated(db, event_data)
        elif event_type == 'customer.subscription.deleted':
            PaymentService.handle_subscription_deleted(db, event_data)
        elif event_type == 'invoice.paid':
            PaymentService.handle_invoice_paid(db, event_data)
        elif event_type == 'invoice.payment_failed':
            PaymentService.handle_invoice_payment_failed(db, event_data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success"}
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


# PayPal Webhook Handler
@router.post("/paypal")
async def paypal_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle PayPal webhook events"""
    try:
        payload = await request.body()
        signature = request.headers.get('PayPal-Transmission-Sig')
        timestamp = request.headers.get('PayPal-Transmission-Time')
        webhook_id = request.headers.get('PayPal-Transmission-Id')
        secret = WEBHOOK_SECRETS['paypal']

        # Validate PayPal signature
        if not _validate_paypal_signature(payload, signature, timestamp, webhook_id, secret):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )

        # Parse event
        event = json.loads(payload)
        event_type = event.get('event_type', '')
        event_resource = event.get('resource', {})

        if event_type == 'CHECKOUT.ORDER.APPROVED':
            PaymentService._handle_payment_succeeded(db, 'paypal', event_resource)
        elif event_type == 'PAYMENT.CAPTURE.DENIED':
            PaymentService._handle_payment_failed(db, 'paypal', event_resource)
        elif event_type == 'BILLING.SUBSCRIPTION.CREATED':
            PaymentService._handle_subscription_created(db, 'paypal', event_resource)
        elif event_type == 'BILLING.SUBSCRIPTION.UPDATED':
            PaymentService._handle_subscription_updated(db, 'paypal', event_resource)
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            PaymentService._handle_subscription_deleted(db, 'paypal', event_resource)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success"}
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


# Mercado Pago Webhook Handler
@router.post("/mercado_pago")
async def mercado_pago_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Mercado Pago webhook events"""
    try:
        payload = await request.body()
        signature = request.headers.get('X-Callback-Signature')
        secret = WEBHOOK_SECRETS['mercado_pago']

        # Validate Mercado Pago signature
        if not _validate_mercado_pago_signature(payload, signature, secret):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )

        # Parse event
        event = json.loads(payload)
        action = event.get('action', '')
        event_data = event.get('data', {}).get('object', {})

        if action == 'payment.created':
            if event_data.get('status') == 'approved':
                PaymentService._handle_payment_succeeded(db, 'mercado_pago', event_data)
            elif event_data.get('status') == 'rejected':
                PaymentService._handle_payment_failed(db, 'mercado_pago', event_data)
        elif action == 'subscription.created':
            PaymentService._handle_subscription_created(db, 'mercado_pago', event_data)
        elif action == 'subscription.updated':
            PaymentService._handle_subscription_updated(db, 'mercado_pago', event_data)
        elif action == 'subscription.deleted':
            PaymentService._handle_subscription_deleted(db, 'mercado_pago', event_data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "success"}
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


# Health Check Endpoint
@router.get("/health")
async def webhooks_health_check():
    """Health check endpoint for webhooks"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'stripe': 'configured' if WEBHOOK_SECRETS['stripe'] != 'YOUR_STRIPE_WEBHOOK_SECRET' else 'not_configured',
                'paypal': 'configured' if WEBHOOK_SECRETS['paypal'] != 'YOUR_PAYPAL_WEBHOOK_SECRET' else 'not_configured',
                'mercado_pago': 'configured' if WEBHOOK_SECRETS['mercado_pago'] != 'YOUR_MERCADO_PAGO_WEBHOOK_SECRET' else 'not_configured'
            }
        }
    )


# Signature Validation Methods
def _validate_stripe_signature(payload: bytes, sig_header: str, secret: str) -> bool:
    """Validate Stripe webhook signature"""
    try:
        # In production, use stripe.Webhook.construct_event
        # This is a placeholder implementation
        if secret == 'YOUR_STRIPE_WEBHOOK_SECRET':
            return True  # Allow in development mode without secret
        return sig_header is not None and len(sig_header) > 0
    except Exception as e:
        print(f"Stripe signature validation failed: {str(e)}")
        return False


def _validate_paypal_signature(payload: bytes, signature: str, timestamp: str, webhook_id: str, secret: str) -> bool:
    """Validate PayPal webhook signature"""
    try:
        # In production, implement proper PayPal signature validation
        # This is a placeholder implementation
        if secret == 'YOUR_PAYPAL_WEBHOOK_SECRET':
            return True  # Allow in development mode without secret
        return signature is not None and len(signature) > 0
    except Exception as e:
        print(f"PayPal signature validation failed: {str(e)}")
        return False


def _validate_mercado_pago_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Validate Mercado Pago webhook signature"""
    try:
        if secret == 'YOUR_MERCADO_PAGO_WEBHOOK_SECRET':
            return True  # Allow in development mode without secret

        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature or '')
    except Exception as e:
        print(f"Mercado Pago signature validation failed: {str(e)}")
        return False
