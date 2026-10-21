import ast
from pathlib import Path

from solution import run_steps

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())


def ok():
    pass


def bad():
    raise ValueError("disk full")


def broken():
    return {}["missing"]


def test_example():
    log = []
    assert run_steps([("backup", ok), ("upload", bad), ("report", ok)], log) == 2, (
        "Return how many steps succeeded.")
    assert log == ["start backup", "done backup", "end backup",
                   "start upload", "failed upload: disk full", "end upload",
                   "start report", "done report", "end report"], f"Got {log}."


def test_no_steps():
    log = []
    assert run_steps([], log) == 0 and log == []


def test_failed_step_has_no_done():
    log = []
    run_steps([("x", bad)], log)
    assert "done x" not in log, (
        "A failed step must not log 'done'. Put the 'done' line in `else`, which runs only on success.")
    assert log == ["start x", "failed x: disk full", "end x"]


def test_other_error_logs_end_then_propagates():
    log = []
    try:
        run_steps([("a", ok), ("b", broken), ("c", ok)], log)
    except KeyError:
        pass
    else:
        raise AssertionError("A KeyError is not a ValueError: it must propagate to the caller.")
    assert log == ["start a", "done a", "end a", "start b", "end b"], (
        f"Got {log}. 'end b' must be logged (finally runs even when the exception propagates), "
        "and step c must not run.")


def test_appends_to_callers_log():
    log = ["earlier"]
    run_steps([("a", ok)], log)
    assert log == ["earlier", "start a", "done a", "end a"], "Append to the caller's list."


def test_uses_finally():
    tries = [n for n in ast.walk(TREE) if isinstance(n, ast.Try)]
    assert any(t.finalbody for t in tries), "Use a `finally` block for the 'end <name>' message."
    for h in ast.walk(TREE):
        if isinstance(h, ast.ExceptHandler):
            assert h.type is not None and ast.unparse(h.type) == "ValueError", "Catch ValueError only."
