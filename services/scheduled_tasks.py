"""
Scheduled Tasks Service for Subscription and Recurring Payments Management System

This module provides scheduled task functionality (cron jobs) using Python's
APScheduler library. It includes tasks for:
- Sending subscription renewal reminders
- Checking for expired subscriptions
- Sending overdue payment notifications
- Generating monthly reports
"""

import os
from datetime import datetime, timedelta
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from main import get_db
from models import Subscription, Payment, User, Plan
from services.email_service import EmailService

class ScheduledTasks:
    """Service to handle scheduled tasks and cron jobs"""
    
    @staticmethod
    def start_scheduler():
        """Start the scheduler to run scheduled tasks"""
        scheduler = BackgroundScheduler()
        
        # Run renewal reminders every day at 8:00 AM
        scheduler.add_job(
            ScheduledTasks.send_renewal_reminders,
            'cron',
            hour=8,
            minute=0,
            id='send_renewal_reminders'
        )
        
        # Run expired subscription check every day at 2:00 AM
        scheduler.add_job(
            ScheduledTasks.check_expired_subscriptions,
            'cron',
            hour=2,
            minute=0,
            id='check_expired_subscriptions'
        )
        
        # Run overdue payment checks every day at 10:00 AM
        scheduler.add_job(
            ScheduledTasks.check_overdue_payments,
            'cron',
            hour=10,
            minute=0,
            id='check_overdue_payments'
        )
        
        # Run monthly report generation on the first day of each month at 3:00 AM
        scheduler.add_job(
            ScheduledTasks.generate_monthly_report,
            'cron',
            day=1,
            hour=3,
            minute=0,
            id='generate_monthly_report'
        )
        
        scheduler.start()
        return scheduler
    
    @staticmethod
    def send_renewal_reminders():
        """Send renewal reminders to users whose subscriptions are expiring soon"""
        db = next(get_db())
        
        try:
            # Find subscriptions expiring in the next 3 days
            expiration_date = datetime.utcnow() + timedelta(days=3)
            
            expiring_subscriptions = db.query(Subscription).filter(
                Subscription.end_date <= expiration_date,
                Subscription.end_date > datetime.utcnow(),
                Subscription.status == "active",
                Subscription.auto_renew == True
            ).all()
            
            for subscription in expiring_subscriptions:
                user = db.query(User).filter(User.id == subscription.user_id).first()
                plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
                
                if user and plan:
                    EmailService.send_subscription_renewal_notification(
                        user.email,
                        plan.name,
                        subscription.end_date
                    )
            
            print(f"Sent {len(expiring_subscriptions)} renewal reminders")
            
        except Exception as e:
            print(f"Error sending renewal reminders: {str(e)}")
        
        finally:
            db.close()
    
    @staticmethod
    def check_expired_subscriptions():
        """Check for expired subscriptions and update their status"""
        db = next(get_db())
        
        try:
            # Find active subscriptions that have expired
            expired_subscriptions = db.query(Subscription).filter(
                Subscription.end_date < datetime.utcnow(),
                Subscription.status == "active"
            ).all()
            
            for subscription in expired_subscriptions:
                subscription.status = "expired"
                db.commit()
                
                # Send notification to user
                user = db.query(User).filter(User.id == subscription.user_id).first()
                plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
                
                if user and plan:
                    EmailService.send_overdue_payment_reminder(
                        user.email,
                        plan.price,
                        subscription.end_date
                    )
            
            print(f"Updated {len(expired_subscriptions)} expired subscriptions")
            
        except Exception as e:
            print(f"Error checking expired subscriptions: {str(e)}")
            db.rollback()
        
        finally:
            db.close()
    
    @staticmethod
    def check_overdue_payments():
        """Check for overdue payments and send notifications"""
        db = next(get_db())
        
        try:
            # Find payments that are pending and overdue (due date was more than 7 days ago)
            overdue_date = datetime.utcnow() - timedelta(days=7)
            
            overdue_payments = db.query(Payment).filter(
                Payment.status == "pending",
                Payment.created_at < overdue_date
            ).all()
            
            for payment in overdue_payments:
                user = db.query(User).filter(User.id == payment.user_id).first()
                
                if user:
                    EmailService.send_overdue_payment_reminder(
                        user.email,
                        payment.amount,
                        payment.created_at
                    )
            
            print(f"Sent {len(overdue_payments)} overdue payment reminders")
            
        except Exception as e:
            print(f"Error checking overdue payments: {str(e)}")
        
        finally:
            db.close()
    
    @staticmethod
    def generate_monthly_report():
        """Generate monthly report of subscription and payment statistics"""
        db = next(get_db())
        
        try:
            # Calculate statistics for the previous month
            now = datetime.utcnow()
            start_date = datetime(now.year, now.month - 1, 1)
            end_date = datetime(now.year, now.month, 1) - timedelta(days=1)
            
            # Calculate number of active subscriptions
            active_subscriptions = db.query(Subscription).filter(
                Subscription.status == "active",
                Subscription.start_date <= end_date
            ).count()
            
            # Calculate number of new subscriptions
            new_subscriptions = db.query(Subscription).filter(
                Subscription.created_at >= start_date,
                Subscription.created_at <= end_date
            ).count()
            
            # Calculate number of cancelled subscriptions
            cancelled_subscriptions = db.query(Subscription).filter(
                Subscription.status == "cancelled",
                Subscription.updated_at >= start_date,
                Subscription.updated_at <= end_date
            ).count()
            
            # Calculate total revenue
            total_revenue = db.query(Payment).filter(
                Payment.status == "succeeded",
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            ).with_entities(
                db.func.sum(Payment.amount)
            ).scalar() or 0
            
            # Calculate number of successful payments
            successful_payments = db.query(Payment).filter(
                Payment.status == "succeeded",
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            ).count()
            
            # Calculate number of failed payments
            failed_payments = db.query(Payment).filter(
                Payment.status == "failed",
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            ).count()
            
            # Generate report content
            report_content = f"""
Monthly Report - {start_date.strftime('%B %Y')}

Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}

Subscription Statistics:
- Active Subscriptions: {active_subscriptions}
- New Subscriptions: {new_subscriptions}
- Cancelled Subscriptions: {cancelled_subscriptions}

Payment Statistics:
- Total Revenue: ${total_revenue:.2f}
- Successful Payments: {successful_payments}
- Failed Payments: {failed_payments}

Overall Health:
- Revenue Growth: {((total_revenue / 10000) * 100) if total_revenue else 0:.2f}% (placeholder)
- Churn Rate: {((cancelled_subscriptions / (active_subscriptions + cancelled_subscriptions)) * 100) if active_subscriptions + cancelled_subscriptions > 0 else 0:.2f}%
            """
            
            # Send report email to admin
            admin_email = os.getenv("ADMIN_EMAIL", "admin@yourdomain.com")
            EmailService.send_email(
                admin_email,
                f"Monthly Report - {start_date.strftime('%B %Y')}",
                report_content
            )
            
            print("Monthly report generated and sent successfully")
            
        except Exception as e:
            print(f"Error generating monthly report: {str(e)}")
        
        finally:
            db.close()