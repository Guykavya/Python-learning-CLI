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
