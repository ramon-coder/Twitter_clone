#!/usr/bin/env python
"""
Configuration validation script.

This script checks if all required environment variables are set
and validates their values for the application.
"""

import os
import sys
from pathlib import Path

# Required environment variables for different environments
REQUIRED_VARS = {
    "always": [
        "SECRET_KEY",
    ],
    "production": [
        "DATABASE_URL",
        "STRIPE_API_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "SENDGRID_API_KEY",
        "EMAIL_SENDER",
        "ADMIN_EMAIL",
    ]
}

OPTIONAL_VARS = [
    "APP_ENV",
    "DEBUG",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "STRIPE_PUBLISHABLE_KEY",
    "PAYPAL_CLIENT_ID",
    "PAYPAL_CLIENT_SECRET",
    "MERCADO_PAGO_ACCESS_TOKEN",
    "AUTH_RATE_LIMIT",
    "AUTH_RATE_WINDOW",
    "SCHEDULER_ENABLED",
    "LOG_LEVEL",
    "LOG_FILE",
]

def check_secret_key():
    """Validate SECRET_KEY length and randomness"""
    secret_key = os.getenv("SECRET_KEY", "")
    if len(secret_key) < 32:
        print("❌ SECRET_KEY is less than 32 characters. Use a longer, random key.")
        return False
    if secret_key in ["your-secret-key-here", "dev-secret-key-change-in-production"]:
        print("❌ SECRET_KEY is using default value. Set a secure random key.")
        return False
    print("✅ SECRET_KEY is properly configured")
    return True

def check_database_url():
    """Validate DATABASE_URL format"""
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        print("⚠️  DATABASE_URL not set (will use SQLite)")
        return True

    app_env = os.getenv("APP_ENV", "development")
    if app_env == "production" and "postgresql" not in db_url:
        print("❌ Production should use PostgreSQL, not SQLite")
        return False

    print("✅ DATABASE_URL is valid")
    return True

def check_email_config():
    """Validate email service configuration"""
    sendgrid_key = os.getenv("SENDGRID_API_KEY", "")
    email_sender = os.getenv("EMAIL_SENDER", "")
    admin_email = os.getenv("ADMIN_EMAIL", "")

    issues = []
    if not sendgrid_key:
        issues.append("SENDGRID_API_KEY not set")
    if not email_sender:
        issues.append("EMAIL_SENDER not set")
    if not admin_email:
        issues.append("ADMIN_EMAIL not set")

    if issues:
        print(f"❌ Email configuration issues: {', '.join(issues)}")
        return False

    print("✅ Email configuration is valid")
    return True

def check_stripe_config():
    """Validate Stripe configuration"""
    stripe_key = os.getenv("STRIPE_API_KEY", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    issues = []
    if not stripe_key:
        issues.append("STRIPE_API_KEY not set")
    if not webhook_secret:
        issues.append("STRIPE_WEBHOOK_SECRET not set")

    if issues:
        print(f"❌ Stripe configuration issues: {', '.join(issues)}")
        return False

    # Validate key format
    if not stripe_key.startswith(("sk_test_", "sk_live_")):
        print("⚠️  STRIPE_API_KEY doesn't start with sk_test_ or sk_live_")

    print("✅ Stripe configuration is valid")
    return True

def check_rate_limiting():
    """Validate rate limiting configuration"""
    rate_limit = os.getenv("AUTH_RATE_LIMIT", "5")
    rate_window = os.getenv("AUTH_RATE_WINDOW", "60")

    try:
        rl = int(rate_limit)
        rw = int(rate_window)
        if rl < 1 or rw < 1:
            print("❌ Rate limiting values must be positive integers")
            return False
        print(f"✅ Rate limiting: {rl} requests per {rw}s")
        return True
    except ValueError:
        print("❌ Rate limiting values must be integers")
        return False

def main():
    """Run all configuration checks"""
    print("🔍 Validating configuration...\n")

    # Load .env if exists
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading .env file")
        from dotenv import load_dotenv
        load_dotenv()

    # Determine environment
    app_env = os.getenv("APP_ENV", "development")
    print(f"🌱 Environment: {app_env}")

    checks = []

    # Always required checks
    checks.append(("SECRET_KEY", check_secret_key()))
    checks.append(("Database", check_database_url()))
    checks.append(("Email", check_email_config()))
    checks.append(("Stripe", check_stripe_config()))
    checks.append(("Rate Limiting", check_rate_limiting()))

    # Check optional variables
    print("\n📋 Optional variables:")
    for var in OPTIONAL_VARS:
        value = os.getenv(var, "Not set")
        if value != "Not set":
            print(f"   ✅ {var} = {value}")
        else:
            print(f"   ⚠️  {var} = Not set (using default)")

    # Production-specific checks
    if app_env == "production":
        print("\n🔒 Production checks:")
        prod_checks = []
        for var in REQUIRED_VARS["production"]:
            if not os.getenv(var):
                print(f"❌ {var} is required in production")
                prod_checks.append(False)
            else:
                print(f"✅ {var} is set")

        checks.extend([(f"Production: {var}", check) for var, check in zip(REQUIRED_VARS["production"], prod_checks)])

    # Summary
    print("\n" + "="*50)
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    print(f"Results: {passed}/{total} checks passed")

    if all(result for _, result in checks):
        print("✅ All critical checks passed! Ready to run.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
