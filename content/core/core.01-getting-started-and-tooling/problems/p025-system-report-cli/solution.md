## Approach

This combines the whole module: shebang, docstring, imports, an environment
variable with a default, `platform` and `sys` facts, a computed `True`/`False`,
and PEP 8 layout.

## Code

```python
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
```

## Why some lines use `+` and others use commas

`print("OS:", a, b)` puts one space between each value, which is exactly the
format wanted. The Python line has brackets with no inner space, so commas would
give `( CPython )`; `+` gives full control.

A long expression can continue on the next line while it is inside brackets.
That keeps the line under 79 characters (PEP 8).

## Another way

An f-string: `print(f"Python: {platform.python_version()} ({platform.python_implementation()})")`
is shorter to think about but too long for one line here; store the two values
in variables first.

## Going further

Make it a real tool: `mkdir ~/code/sysinfo`, create a venv, copy the script as
`sysinfo.py`, `chmod +x sysinfo.py`, add `.venv/` to `.gitignore`, and commit.
Run `echo Kav | ./sysinfo.py` to feed the nickname through a pipe.
