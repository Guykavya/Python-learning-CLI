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
