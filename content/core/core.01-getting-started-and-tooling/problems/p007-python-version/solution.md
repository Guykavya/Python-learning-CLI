## Approach

Ask the running interpreter about itself. `sys.version_info` holds the version
as separate numbers; `platform.python_version()` gives it as text.

## Code

```python
import platform
import sys

print("Major:", sys.version_info.major)
print("Minor:", sys.version_info.minor)
print("Full:", platform.python_version())
```

## Why

A script can be run by different interpreters (system Python, a venv, a pyenv
version). Asking at run time always reports the one that is really running.

## Another way

`sys.version_info[0]` and `sys.version_info[1]` work too, because `version_info`
also behaves like a sequence. `sys.version` gives a long text with build details.
