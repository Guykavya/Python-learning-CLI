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
