## Hint 1

Which lines can be printed with `print("Label:", value)`, and which one needs
exact control over spaces?

## Hint 2

For the Python line, join strings with `+`: `"Python: " + version + " (" +
implementation + ")"`. `platform.python_version()` already returns a `str`, so
no conversion is needed. Store long expressions in variables first to keep
lines under 79 characters.

## Hint 3

```
#!/usr/bin/env python3
"""<one sentence about the script>"""
import os, platform, sys (one per line)
nickname = input()
border = "=" * 30
user = os.environ.get("USER", "unknown")
print border, "System report for" + nickname, border
print User, Python (joined with +), OS (two values), Machine, Folder
print("In venv:", sys.prefix != sys.base_prefix)
print border
```
