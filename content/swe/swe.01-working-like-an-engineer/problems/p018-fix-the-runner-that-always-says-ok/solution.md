## Approach

The three bugs and their fixes:

1. `PY = ["python", "-m"]` starts whatever `python` is first on the `PATH`, perhaps not the virtual environment's: use `sys.executable`.
2. `run(cmd)` throws the exit code away, so the loop never stops and `main` always returns 0: CI sees success even when pytest failed. Fix: `code = run(cmd)`, then `if code != 0: return code`.
3. `check` lists `test` first. The cheap, fast checks (lint, types) should run first so a trivial mistake is reported in seconds.

```python
import sys

PY = [sys.executable, "-m"]

TASKS = {
    "test": [[*PY, "pytest"]],
    "lint": [[*PY, "ruff", "check", "."], [*PY, "ruff", "format", "--check", "."]],
    "types": [[*PY, "mypy"]],
}
TASKS["check"] = TASKS["lint"] + TASKS["types"] + TASKS["test"]


def main(argv, run):
    if len(argv) != 2 or argv[1] not in TASKS:
        print("usage: python tasks.py <task>")
        for name in TASKS:
            print("  " + name)
        return 2
    for cmd in TASKS[argv[1]]:
        code = run(cmd)
        if code != 0:
            return code
    return 0
```

## Why CI went green

CI looks at the **exit code** of `python tasks.py check`. Because `main` returned 0 whatever happened, the exit code was 0, and a pipeline that only checks that code reported success. Always propagate the failing code.

## Complexity

Not applicable.

## Another way

`subprocess.run(cmd, check=True)` raises on failure and cannot be ignored by accident; the injected `run` here returns a code, so the caller has to check it explicitly.
