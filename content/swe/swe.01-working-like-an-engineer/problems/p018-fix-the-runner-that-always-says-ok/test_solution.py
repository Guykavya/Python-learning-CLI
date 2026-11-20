import sys

from solution import main

PY = sys.executable
LINT = [[PY, "-m", "ruff", "check", "."], [PY, "-m", "ruff", "format", "--check", "."]]
TYPES = [[PY, "-m", "mypy"]]
TEST = [[PY, "-m", "pytest"]]


def go(task, fail_at=None, code=1):
    """Run main with a fake run(): returns (exit code, recorded commands). The call number fail_at fails."""
    calls = []

    def run(cmd):
        calls.append(list(cmd))
        return code if fail_at is not None and len(calls) - 1 == fail_at else 0

    argv = ["tasks.py"] + ([task] if task else [])
    return main(argv, run), calls


def test_commands_use_the_running_interpreter():
    for cmd in go("check")[1]:
        assert cmd[0] == sys.executable, (
            f"Bug 1: the command starts with {cmd[0]!r}. Use sys.executable: the Python that is running you.")


def test_a_failing_command_is_reported():
    code, calls = go("test", fail_at=0, code=1)
    assert code == 1, (
        "Bug 2: main returned 0 although pytest failed. run() returns the exit code: check it and return it.")


def test_stop_at_the_first_failure():
    code, calls = go("lint", fail_at=0, code=4)
    assert code == 4 and len(calls) == 1, "After the first failing command, do not run the next one."


def test_check_order_is_lint_types_test():
    assert go("check")[1] == LINT + TYPES + TEST, (
        "Bug 3: check must run the cheap checks first: lint, then types, then the slow tests.")


def test_check_stops_before_the_tests_when_lint_fails():
    code, calls = go("check", fail_at=0, code=1)
    assert code == 1 and calls == LINT[:1], "A lint error must stop check at once, before types and tests."


def test_success_returns_zero_and_unknown_task_returns_two(capsys):
    assert go("test")[0] == 0
    code, calls = go("deploy")
    out = capsys.readouterr().out
    assert code == 2 and calls == [] and out.splitlines()[0] == "usage: python tasks.py <task>"
