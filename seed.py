"""Development database seeding script.

This script creates initial data for development and testing environments.
Run with: python seed.py
"""

import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from main import engine, get_db
from models import User, Plan, Subscription, Base

def seed_database():
    """Seed the database with initial test data"""
    db = next(get_db())

    try:
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96pCT9NZwWG0NB9MhO.C6m5JKy",  # "secret"
            full_name="Admin User",
            phone_number="+1234567890",
            is_active=True,
            is_admin=True
        )
        db.add(admin_user)

        # Create test user
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96pCT9NZwWG0NB9MhO.C6m5JKy",  # "secret"
            full_name="Test User",
            phone_number="+1234567891",
            is_active=True,
            is_admin=False
        )
        db.add(test_user)

        # Create subscription plans
        basic_plan = Plan(
            name="Basic",
            description="Basic subscription plan with essential features",
            price=9.99,
            duration=30,
            features='{"support": "email", "storage": "10GB", "users": 1}',
            is_active=True
        )
        db.add(basic_plan)

        premium_plan = Plan(
            name="Premium",
            description="Premium subscription plan with advanced features",
            price=29.99,
            duration=30,
            features='{"support": "24/7", "storage": "100GB", "users": 5}',
            is_active=True
        )
        db.add(premium_plan)

        enterprise_plan = Plan(
            name="Enterprise",
            description="Enterprise plan with unlimited features",
            price=99.99,
            duration=30,
            features='{"support": "dedicated", "storage": "unlimited", "users": "unlimited"}',
            is_active=True
        )
        db.add(enterprise_plan)

        db.commit()

        # Create a test subscription for test user
        basic_plan_db = db.query(Plan).filter(Plan.name == "Basic").first()
        if basic_plan_db:
            subscription = Subscription(
                user_id=test_user.id,
                plan_id=basic_plan_db.id,
                start_date=datetime.utcnow() - timedelta(days=15),
                end_date=datetime.utcnow() + timedelta(days=15),
                status="active",
                auto_renew=True
            )
            db.add(subscription)

        db.commit()

        print("✅ Database seeded successfully!")
        print(f"   - Admin user: admin@example.com / secret")
        print(f"   - Test user: test@example.com / secret")
        print(f"   - Plans created: Basic, Premium, Enterprise")

    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Only run in development mode
    if os.getenv("APP_ENV", "development") != "production":
        seed_database()
    else:
        print("⚠️  Seeding is not allowed in production!")
