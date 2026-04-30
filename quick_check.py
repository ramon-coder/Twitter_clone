#!/usr/bin/env python
"""Quick syntax check for main.py"""

import ast
import sys

try:
    with open("main.py", "r", encoding="utf-8") as f:
        source = f.read()
    ast.parse(source)
    print("[OK] main.py syntax valid")
    sys.exit(0)
except SyntaxError as e:
    print(f"[ERROR] Syntax error in main.py: {e}")
    sys.exit(1)
