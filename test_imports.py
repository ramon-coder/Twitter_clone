#!/usr/bin/env python
"""Test imports for all modules"""

import sys
import traceback

modules = [
    "main",
    "routers.auth",
    "routers.plans",
    "routers.users",
    "routers.subscriptions",
    "routers.payments",
    "routers.webhooks",
    "models.user",
    "models.plan",
    "models.subscription",
    "models.payment",
    "models.invoice",
    "services.payment_service",
    "services.email_service",
    "services.scheduled_tasks",
    "middleware.rate_limit",
]

print("Testing imports...")
failed = []

for module in modules:
    try:
        __import__(module)
        print(f"[OK] {module}")
    except Exception as e:
        print(f"[FAIL] {module}: {e}")
        failed.append(module)

if failed:
    print(f"\n{len(failed)} modules failed to import")
    sys.exit(1)
else:
    print(f"\nAll {len(modules)} modules imported successfully!")
    sys.exit(0)
