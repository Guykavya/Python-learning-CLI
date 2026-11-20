## Approach

```python
import sys

_PY = [sys.executable, "-m"]

TASKS = {
    "test": ("run the tests", [[*_PY, "pytest"]]),
    "lint": ("check style with ruff", [[*_PY, "ruff", "check", "."], [*_PY, "ruff", "format", "--check", "."]]),
    "types": ("check type hints with mypy", [[*_PY, "mypy"]]),
}
TASKS["check"] = ("lint, types and tests", TASKS["lint"][1] + TASKS["types"][1] + TASKS["test"][1])


def main(argv, run):
    if len(argv) != 2 or argv[1] not in TASKS:
        print("usage: python tasks.py <task>")
        for name, (doc, _) in TASKS.items():
            print(f"  {name:6} {doc}")
        return 2
    for cmd in TASKS[argv[1]][1]:
        code = run(cmd)
        if code != 0:
            return code
    return 0
```

Tasks are data (a list of commands) and one loop runs them, so `check` is just three lists joined: the order `lint, types, test` is the order of cost (fast failures first). The injected `run` is what makes the runner testable: a test passes a function that records commands and returns a chosen exit code; the real `tasks.py` would pass `subprocess.call`.

Example: `main(["tasks.py", "check"], run)` where the 3rd command fails with code 1: calls 1 and 2 (`ruff check`, `ruff format --check`) succeed, call 3 (`mypy`) returns 1, and `main` returns 1 without running `pytest`.

## Complexity

`O(number of commands)`.

## Another way

A Makefile does the same with targets; the pure-Python version works on Windows too (chapter section 13) and its logic can be unit-tested, as here.

## Why it matters

A task runner that ignores exit codes makes CI green with failing tests (see the next problem). Returning the first failing code makes the failure visible to the shell and to CI.
