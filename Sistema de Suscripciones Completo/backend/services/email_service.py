"""
Email Service for Subscription and Recurring Payments Management System

This module provides email notification functionality using SendGrid. It
supports sending various types of emails related to subscriptions and payments:
- Payment confirmations
- Payment failures
- Subscription renewals
- Subscription cancellations
- Overdue payment reminders
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailService:
    """Service to handle email notifications"""
    
    # Initialize SendGrid client with API key from environment
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    
    @staticmethod
    def send_email(to_email: str, subject: str, body: str):
        """
        Send an email using SendGrid.
        
        Args:
            to_email: Recipient's email address
            subject: Email subject
            body: Email body content
            
        Returns:
            Response from SendGrid API
        """
        from_email = os.getenv("EMAIL_SENDER", "no-reply@yourdomain.com")
        
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        
        try:
            response = EmailService.sg.send(message)
            return response
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return None
    
    @staticmethod
    def send_payment_confirmation(user_email: str, payment_amount: float, payment_date: datetime):
        """
        Send a payment confirmation email.
        
        Args:
            user_email: Recipient's email address
            payment_amount: Amount paid
            payment_date: Date of payment
        """
        subject = "Payment Confirmation"
        body = f"""
Hello,

Your payment of ${payment_amount:.2f} has been successfully processed on {payment_date.strftime('%Y-%m-%d')}.

Thank you for your subscription!

Regards,
The Subscription Team
        """
        
        return EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    def send_payment_failed(user_email: str, payment_amount: float, failure_reason: str):
        """
        Send a payment failed email.
        
        Args:
            user_email: Recipient's email address
            payment_amount: Amount that failed to process
            failure_reason: Reason for payment failure
        """
        subject = "Payment Failed"
        body = f"""
Hello,

We were unable to process your payment of ${payment_amount:.2f}.

Reason for failure: {failure_reason}

Please update your payment information to avoid service interruption.

Regards,
The Subscription Team
        """
        
        return EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    def send_subscription_renewal_notification(user_email: str, plan_name: str, renewal_date: datetime):
        """
        Send a subscription renewal notification.
        
        Args:
            user_email: Recipient's email address
            plan_name: Name of the subscription plan
            renewal_date: Date of the next renewal
        """
        subject = "Subscription Renewal Reminder"
        body = f"""
Hello,

Your {plan_name} subscription is scheduled to renew on {renewal_date.strftime('%Y-%m-%d')}.

We will automatically charge your payment method on file for the next billing cycle.

If you wish to cancel your subscription, please visit your account settings before the renewal date.

Regards,
The Subscription Team
        """
        
        return EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    def send_subscription_cancelled(user_email: str, plan_name: str, cancel_date: datetime):
        """
        Send a subscription cancellation email.
        
        Args:
            user_email: Recipient's email address
            plan_name: Name of the cancelled subscription plan
            cancel_date: Date of cancellation
        """
        subject = "Subscription Cancelled"
        body = f"""
Hello,

Your {plan_name} subscription has been successfully cancelled on {cancel_date.strftime('%Y-%m-%d')}.

You will continue to have access to your subscription benefits until your current billing period ends.

If you change your mind, you can reactivate your subscription at any time.

Regards,
The Subscription Team
        """
        
        return EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    def send_overdue_payment_reminder(user_email: str, amount_due: float, due_date: datetime):
        """
        Send an overdue payment reminder.
        
        Args:
            user_email: Recipient's email address
            amount_due: Amount that is overdue
            due_date: Original due date of payment
        """
        subject = "Overdue Payment Reminder"
        body = f"""
Hello,

Your payment of ${amount_due:.2f} is now overdue. The original due date was {due_date.strftime('%Y-%m-%d')}.

Please update your payment information to avoid service interruption.

Regards,
The Subscription Team
        """
        
        return EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    def send_trial_ending_notification(user_email: str, plan_name: str, trial_end_date: datetime):
        """
        Send a trial ending notification.
        
        Args:
            user_email: Recipient's email address
            plan_name: Name of the trial plan
            trial_end_date: Date when the trial ends
        """
        subject = "Trial Ending Soon"
        body = f"""
Hello,

Your {plan_name} trial subscription is ending soon. The trial will end on {trial_end_date.strftime('%Y-%m-%d')}.

To continue accessing your subscription benefits after the trial period, please update your payment information.

If you do not wish to continue, your subscription will automatically cancel at the end of the trial.

Regards,
The Subscription Team
        """
        
        return EmailService.send_email(user_email, subject, body)
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str):
        """
        Send a welcome email to new users.
        
        Args:
            user_email: Recipient's email address
            user_name: Name of the new user
        """
        subject = "Welcome to Our Subscription Service"
        body = f"""
Hello {user_name},

Welcome to our subscription service! We're excited to have you on board.

Here's what you can expect:
- Access to all features of your chosen plan
- Regular updates and improvements
- 24/7 customer support

If you have any questions, please don't hesitate to contact us.

Regards,
The Subscription Team
        """
        
        return EmailService.send_email(user_email, subject, body)