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


def test_single_tasks_run_their_commands():
    assert go("test") == (0, TEST)
    assert go("types") == (0, TYPES)
    assert go("lint") == (0, LINT), "lint runs 'ruff check .' and then 'ruff format --check .'."


def test_check_runs_lint_types_test_in_that_order():
    code, calls = go("check")
    assert code == 0
    assert calls == LINT + TYPES + TEST, "check = lint (both commands), then types, then tests: cheap checks first."


def test_commands_use_sys_executable_not_the_word_python():
    for task in ("test", "lint", "types", "check"):
        for cmd in go(task)[1]:
            assert cmd[0] == sys.executable and cmd[1] == "-m", (
                f"Start every command with sys.executable and '-m', not 'python'. Got {cmd}.")


def test_stops_at_the_first_failure_and_returns_its_code():
    code, calls = go("check", fail_at=1, code=3)    # 'ruff format --check' fails with 3
    assert code == 3, "Return the exit code of the failing command."
    assert calls == LINT, "Do not run types or tests after a failure."
    code, calls = go("check", fail_at=2, code=1)    # mypy fails
    assert (code, calls) == (1, LINT + TYPES)
    code, calls = go("lint", fail_at=0, code=5)
    assert (code, len(calls)) == (5, 1), "If 'ruff check' fails, 'ruff format --check' is not run."


def test_failure_of_the_only_command():
    assert go("test", fail_at=0, code=2) == (2, TEST)


def test_unknown_or_missing_task_prints_usage_and_returns_2(capsys):
    for task in ("nothing", None):
        code, calls = go(task)
        out = capsys.readouterr().out
        assert code == 2 and calls == [], "No command may run for an unknown task; return 2."
        assert out.splitlines()[0] == "usage: python tasks.py <task>", "The first line is the usage line."
        for name in ("test", "lint", "types", "check"):
            assert any(line.strip().startswith(name) for line in out.splitlines()[1:]), f"List the task {name}."


def test_extra_arguments_are_a_usage_error(capsys):
    calls = []
    assert main(["tasks.py", "test", "extra"], lambda c: calls.append(c) or 0) == 2 and calls == []
