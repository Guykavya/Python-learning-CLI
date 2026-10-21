## Approach

Add the shebang as line 1, then print the two special names.

## Code

```python
#!/usr/bin/env python3
import os

print("Running as:", __name__)
print("Script file:", os.path.basename(__file__))
```

## Why it works

- `./solution.py` makes the kernel read the first line. `#!` means "run this
  file with the program named here". `/usr/bin/env python3` finds `python3` on
  `PATH`, so an active venv's Python is used.
- To Python, line 1 is just a comment, so `python3 solution.py` works too.
- `__name__` is `"__main__"` for the file you run directly.
- `__file__` is the script's path; `basename` strips the folders.

## Another way

`#!/usr/bin/python3` also runs, but always uses the system Python, ignoring
your venv. Prefer `env`.
