import os

from solution import measure

GRADE = """def grade(n):
    if n >= 90:
        return "A"
    if n >= 50:
        return "B"
    return "F"
"""

RATIO = """def ratio(a, b):
    if b == 0:
        raise ValueError("b is zero")
    return a / b
"""

WITH_CONSTANT = """LIMIT = 10

def check(n):
    if n > LIMIT:
        return "big"
    return "small"
"""


def test_some_lines_are_never_run():
    assert measure(GRADE, "grade", [(95,), (10,)]) == (83.3, [5]), (
        "grade(95) runs the 'A' return and grade(10) runs the 'F' return. Line 5 (return \"B\") never runs: "
        "5 of 6 statements = 83.3 percent, missing [5].")


def test_every_line_is_run():
    assert measure(GRADE, "grade", [(95,), (60,), (10,)]) == (100.0, []), (
        "Three calls reach all three returns: 100.0 percent and an empty list of missing lines.")


def test_no_calls_only_the_def_line_runs():
    assert measure(GRADE, "grade", []) == (16.7, [2, 3, 4, 5, 6]), (
        "With no calls only the 'def' line runs (when the module is imported): 1 of 6 = 16.7 percent. "
        "Start coverage BEFORE you import the module, or the def line is counted as missing.")


def test_a_raising_call_does_not_stop_the_measurement():
    assert measure(RATIO, "ratio", [(1, 0), (6, 3)]) == (100.0, []), (
        "ratio(1, 0) raises ValueError. Catch the exception and carry on with the next call: "
        "the raise line was executed, and ratio(6, 3) reaches the last line.")
    assert measure(RATIO, "ratio", [(1, 0)]) == (75.0, [4]), "Only the failing call: line 4 is missing."


def test_module_level_statements_count_too():
    assert measure(WITH_CONSTANT, "check", [(1,)]) == (80.0, [5]), (
        "Statements outside the function (LIMIT = 10) are part of the file and count as run.")


def test_result_types_and_repeatability():
    first = measure(GRADE, "grade", [(95,)])
    again = measure(GRADE, "grade", [(95,)])
    assert first == again, "Two identical measurements must give identical results (no state kept between them)."
    percent, missing = first
    assert isinstance(percent, float) and isinstance(missing, list), "Return (float percent, list of line numbers)."
    assert missing == sorted(missing) and all(isinstance(n, int) for n in missing), "Missing lines: sorted ints."


def test_no_coverage_file_is_left_behind(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    measure(GRADE, "grade", [(95,)])
    leftovers = sorted(p.name for p in tmp_path.iterdir())
    assert leftovers == [], (
        f"Your function left files in the current folder: {leftovers}. Create the Coverage object with data_file=None "
        "and put the temporary source file in a TemporaryDirectory.")
