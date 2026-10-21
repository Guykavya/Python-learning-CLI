## Approach

Each fact is one attribute or one function call. Print them with a label.

## Code

```python
import os
import platform
import sys

print("Executable:", sys.executable)
print("Version:", platform.python_version())
print("Implementation:", platform.python_implementation())
print("System:", platform.system())
print("Folder:", os.getcwd())
```

## Why it is useful

- If `Executable` is not inside your `.venv`, your venv is not being used.
- `os.getcwd()` is where you ran the command from. Relative file paths in your
  programs are resolved from there, not from the script's folder.

## Another way

`platform.platform()` gives one long description of the OS. `sys.version` gives
the version with build details.
