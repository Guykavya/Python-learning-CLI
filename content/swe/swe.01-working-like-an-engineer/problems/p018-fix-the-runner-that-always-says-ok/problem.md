# Fix the runner that always says OK

The team's `tasks.py` made CI **green with failing tests**. This is its `main` (same interface as the previous problem: `main(argv, run)`, `run(cmd)` returns an exit code):

```python
import sys

PY = ["python", "-m"]

TASKS = {
    "test": [[*PY, "pytest"]],
    "lint": [[*PY, "ruff", "check", "."], [*PY, "ruff", "format", "--check", "."]],
    "types": [[*PY, "mypy"]],
}
TASKS["check"] = TASKS["test"] + TASKS["lint"] + TASKS["types"]


def main(argv, run):
    if len(argv) != 2 or argv[1] not in TASKS:
        print("usage: python tasks.py <task>")
        for name in TASKS:
            print("  " + name)
        return 2
    for cmd in TASKS[argv[1]]:
        run(cmd)
    return 0
```

It has **three bugs**. Fix them in `solution.py` (start from `starter.py`, which has this code). The required behaviour:

- every command starts with `sys.executable` and `-m`;
- the run **stops at the first command that fails** and `main` returns that exit code (0 on success);
- `check` runs `lint`, then `types`, then `test`;
- an unknown task prints a usage text (the line `usage: python tasks.py <task>` first) and returns 2.

Do not rewrite it from scratch: find the three bugs.
