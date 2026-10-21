#!/usr/bin/env python3
"""Print a short report about this computer and the Python running it."""
import os
import platform
import sys

nickname = input()
border = "=" * 30
user = os.environ.get("USER", "unknown")
in_venv = sys.prefix != sys.base_prefix

print(border)
print("System report for", nickname)
print(border)
print("User:", user)
print("Python: " + platform.python_version()
      + " (" + platform.python_implementation() + ")")
print("OS:", platform.system(), platform.release())
print("Machine:", platform.machine())
print("Folder:", os.getcwd())
print("In venv:", in_venv)
print(border)
