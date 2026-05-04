#!/usr/bin/env python
"""Validate Python syntax for all modules."""

import py_compile
import sys
from pathlib import Path

def check_file(filepath: Path) -> bool:
    """Check syntax of a Python file"""
    try:
        py_compile.compile(str(filepath), doraise=True)
        print(f"[OK] {filepath}")
        return True
    except py_compile.PyCompileError as e:
        print(f"[ERROR] {filepath}: {e}")
        return False

def main():
    """Check syntax for critical files"""
    base = Path(__file__).parent

    files_to_check = [
        "main.py",
        "routers/auth.py",
        "routers/plans.py",
        "routers/subscriptions.py",
        "routers/payments.py",
        "routers/users.py",
        "routers/webhooks.py",
        "models/__init__.py",
        "models/user.py",
        "models/plan.py",
        "models/subscription.py",
        "models/payment.py",
        "models/invoice.py",
        "services/payment_service.py",
        "services/email_service.py",
        "services/scheduled_tasks.py",
        "middleware/rate_limit.py",
        "seed.py",
        "check_config.py",
        "exceptions.py",
    ]

    print("Validating Python syntax...\n")

    all_passed = True
    for file in files_to_check:
        filepath = base / file
        if filepath.exists():
            if not check_file(filepath):
                all_passed = False
        else:
            print(f"[WARN] {file} - File not found")
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] All syntax checks passed!")
        return 0
    else:
        print("\n[FAIL] Some files have syntax errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())
