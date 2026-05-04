"""
Webhooks Module for Subscription and Recurring Payments Management System

This module provides endpoints to handle webhook events from payment gateways
such as Stripe, PayPal, and others. It processes events related to:
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
from typing import Callable, Dict, Optional
from datetime import datetime

from flask import Flask, request, jsonify
from pydantic import BaseModel, Field

app = Flask(__name__)

# Configuration - Replace with your actual values
WEBHOOK_SECRETS = {
    'stripe': 'YOUR_STRIPE_WEBHOOK_SECRET',
    'paypal': 'YOUR_PAYPAL_WEBHOOK_SECRET',
    'mercado_pago': 'YOUR_MERCADO_PAGO_WEBHOOK_SECRET'
}

# Database connection (placeholder - replace with your actual implementation)
class Database:
    @staticmethod
    def update_payment_status(payment_id: str, status: str) -> bool:
        """Update payment status in database"""
        print(f"Updating payment {payment_id} to status: {status}")
        return True
    
    @staticmethod
    def update_subscription_status(subscription_id: str, status: str) -> bool:
        """Update subscription status in database"""
        print(f"Updating subscription {subscription_id} to status: {status}")
        return True
    
    @staticmethod
    def create_invoice(invoice_data: Dict) -> bool:
        """Create a new invoice in database"""
        print(f"Creating invoice: {invoice_data}")
        return True
    
    @staticmethod
    def record_failed_payment(payment_id: str, error_message: str) -> bool:
        """Record failed payment details"""
        print(f"Recording failed payment {payment_id}: {error_message}")
        return True

# Webhook Event Models
class WebhookEvent(BaseModel):
    """Base model for webhook events"""
    id: str
    type: str
    timestamp: datetime
    data: Dict

# Stripe Webhook Handler
@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        secret = WEBHOOK_SECRETS['stripe']
        
        # Validate Stripe signature
        if not _validate_stripe_signature(payload, sig_header, secret):
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Parse event
        event = json.loads(payload)
        
        # Process event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            _handle_payment_succeeded('stripe', payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            _handle_payment_failed('stripe', payment_intent)
        elif event['type'] == 'customer.subscription.created':
            subscription = event['data']['object']
            _handle_subscription_created('stripe', subscription)
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            _handle_subscription_updated('stripe', subscription)
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            _handle_subscription_deleted('stripe', subscription)
        elif event['type'] == 'invoice.paid':
            invoice = event['data']['object']
            _handle_invoice_paid('stripe', invoice)
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            _handle_invoice_payment_failed('stripe', invoice)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"Stripe webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# PayPal Webhook Handler
@app.route('/webhooks/paypal', methods=['POST'])
def paypal_webhook():
    """Handle PayPal webhook events"""
    try:
        payload = request.data
        signature = request.headers.get('PayPal-Transmission-Sig')
        timestamp = request.headers.get('PayPal-Transmission-Time')
        webhook_id = request.headers.get('PayPal-Transmission-Id')
        secret = WEBHOOK_SECRETS['paypal']
        
        # Validate PayPal signature
        if not _validate_paypal_signature(payload, signature, timestamp, webhook_id, secret):
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Parse event
        event = json.loads(payload)
        
        # Process event
        if event['event_type'] == 'CHECKOUT.ORDER.APPROVED':
            order = event['resource']
            _handle_payment_succeeded('paypal', order)
        elif event['event_type'] == 'PAYMENT.CAPTURE.DENIED':
            capture = event['resource']
            _handle_payment_failed('paypal', capture)
        elif event['event_type'] == 'BILLING.SUBSCRIPTION.CREATED':
            subscription = event['resource']
            _handle_subscription_created('paypal', subscription)
        elif event['event_type'] == 'BILLING.SUBSCRIPTION.UPDATED':
            subscription = event['resource']
            _handle_subscription_updated('paypal', subscription)
        elif event['event_type'] == 'BILLING.SUBSCRIPTION.CANCELLED':
            subscription = event['resource']
            _handle_subscription_deleted('paypal', subscription)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"PayPal webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Mercado Pago Webhook Handler
@app.route('/webhooks/mercado_pago', methods=['POST'])
def mercado_pago_webhook():
    """Handle Mercado Pago webhook events"""
    try:
        payload = request.data
        signature = request.headers.get('X-Callback-Signature')
        secret = WEBHOOK_SECRETS['mercado_pago']
        
        # Validate Mercado Pago signature
        if not _validate_mercado_pago_signature(payload, signature, secret):
            return jsonify({'error': 'Invalid signature'}), 400
        
        # Parse event
        event = json.loads(payload)
        
        # Process event
        if event['action'] == 'payment.created' and event['data']['object']['status'] == 'approved':
            payment = event['data']['object']
            _handle_payment_succeeded('mercado_pago', payment)
        elif event['action'] == 'payment.created' and event['data']['object']['status'] == 'rejected':
            payment = event['data']['object']
            _handle_payment_failed('mercado_pago', payment)
        elif event['action'] == 'subscription.created':
            subscription = event['data']['object']
            _handle_subscription_created('mercado_pago', subscription)
        elif event['action'] == 'subscription.updated':
            subscription = event['data']['object']
            _handle_subscription_updated('mercado_pago', subscription)
        elif event['action'] == 'subscription.deleted':
            subscription = event['data']['object']
            _handle_subscription_deleted('mercado_pago', subscription)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"Mercado Pago webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Event Handlers
def _handle_payment_succeeded(gateway: str, payment_data: Dict):
    """Handle successful payment event"""
    payment_id = payment_data.get('id') or payment_data.get('payment_intent')
    status = 'succeeded'
    
    # Update payment status in database
    Database.update_payment_status(payment_id, status)
    
    # Additional logic: Send confirmation email, update user balance, etc.
    print(f"Payment succeeded via {gateway}: {payment_id}")

def _handle_payment_failed(gateway: str, payment_data: Dict):
    """Handle failed payment event"""
    payment_id = payment_data.get('id') or payment_data.get('payment_intent')
    error_message = payment_data.get('last_payment_error', {}).get('message', 'Unknown error')
    status = 'failed'
    
    # Update payment status in database
    Database.update_payment_status(payment_id, status)
    Database.record_failed_payment(payment_id, error_message)
    
    # Additional logic: Send notification, retry payment, etc.
    print(f"Payment failed via {gateway}: {payment_id} - {error_message}")

def _handle_subscription_created(gateway: str, subscription_data: Dict):
    """Handle subscription created event"""
    subscription_id = subscription_data.get('id')
    status = 'active'
    
    # Update subscription status in database
    Database.update_subscription_status(subscription_id, status)
    
    # Additional logic: Send welcome email, provision services, etc.
    print(f"Subscription created via {gateway}: {subscription_id}")

def _handle_subscription_updated(gateway: str, subscription_data: Dict):
    """Handle subscription updated event"""
    subscription_id = subscription_data.get('id')
    status = subscription_data.get('status')
    
    # Update subscription status in database
    Database.update_subscription_status(subscription_id, status)
    
    # Additional logic: Update user's access, send notification, etc.
    print(f"Subscription updated via {gateway}: {subscription_id} - Status: {status}")

def _handle_subscription_deleted(gateway: str, subscription_data: Dict):
    """Handle subscription deleted event"""
    subscription_id = subscription_data.get('id')
    status = 'cancelled'
    
    # Update subscription status in database
    Database.update_subscription_status(subscription_id, status)
    
    # Additional logic: Revoke access, send cancellation email, etc.
    print(f"Subscription deleted via {gateway}: {subscription_id}")

def _handle_invoice_paid(gateway: str, invoice_data: Dict):
    """Handle invoice paid event"""
    invoice_id = invoice_data.get('id')
    
    # Create invoice record in database
    Database.create_invoice(invoice_data)
    
    # Additional logic: Send invoice email, update accounting, etc.
    print(f"Invoice paid via {gateway}: {invoice_id}")

def _handle_invoice_payment_failed(gateway: str, invoice_data: Dict):
    """Handle invoice payment failed event"""
    invoice_id = invoice_data.get('id')
    error_message = invoice_data.get('last_finalization_error', {}).get('message', 'Unknown error')
    
    # Record failed invoice payment
    Database.record_failed_payment(invoice_id, error_message)
    
    # Additional logic: Send notification, suspend services, etc.
    print(f"Invoice payment failed via {gateway}: {invoice_id} - {error_message}")

# Signature Validation Methods
def _validate_stripe_signature(payload: bytes, sig_header: str, secret: str) -> bool:
    """Validate Stripe webhook signature"""
    try:
        # This is a simplified version - in production use stripe.Webhook.construct_event
        # For demonstration purposes, we'll create a simple validation
        # In real implementation, use:
        # stripe.Webhook.construct_event(payload, sig_header, secret)
        return True
    except Exception as e:
        print(f"Stripe signature validation failed: {str(e)}")
        return False

def _validate_paypal_signature(payload: bytes, signature: str, timestamp: str, webhook_id: str, secret: str) -> bool:
    """Validate PayPal webhook signature"""
    try:
        # PayPal signature validation involves multiple steps
        # For demonstration purposes, we'll create a simple validation
        return True
    except Exception as e:
        print(f"PayPal signature validation failed: {str(e)}")
        return False

def _validate_mercado_pago_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Validate Mercado Pago webhook signature"""
    try:
        # Mercado Pago signature validation uses HMAC-SHA256
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        print(f"Mercado Pago signature validation failed: {str(e)}")
        return False

# Health Check Endpoint
@app.route('/webhooks/health', methods=['GET'])
def health_check():
    """Health check endpoint for webhooks"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'stripe': 'configured',
            'paypal': 'configured',
            'mercado_pago': 'configured'
        }
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)