import ast
from pathlib import Path

import pytest

import solution
from solution import legacy_report

# (name, rows, expected report). Expected strings are real output of the ORIGINAL legacy_report.
CASES = [
    ('empty', [], 'REPORT\nno data'),
    ('one_paid', [{'name': 'Ana', 'dept': 'eng', 'amount': 100, 'status': 'paid'}], 'REPORT\n== Eng ==\n  rows: 1  paid: 100.00  pending: 0.00\n  top: Ana (100.00)\nTOTAL paid: 100.00  pending: 0.00'),
    ('one_pending', [{'name': 'Bo', 'dept': 'ops', 'amount': 20.5, 'status': 'pending'}], 'REPORT\n== Ops ==\n  rows: 1  paid: 0.00  pending: 20.50\n  top: Bo (20.50)\nTOTAL paid: 0.00  pending: 20.50'),
    ('two_depts', [{'name': 'Ana', 'dept': 'eng', 'amount': 100, 'status': 'paid'}, {'name': 'Bo', 'dept': 'ops', 'amount': 20.5, 'status': 'pending'}, {'name': 'Cy', 'dept': 'eng', 'amount': 50, 'status': 'pending'}], 'REPORT\n== Eng ==\n  rows: 2  paid: 100.00  pending: 50.00\n  top: Ana (100.00)\n== Ops ==\n  rows: 1  paid: 0.00  pending: 20.50\n  top: Bo (20.50)\nTOTAL paid: 100.00  pending: 70.50'),
    ('tie_alpha', [{'name': 'Zed', 'dept': 'eng', 'amount': 70, 'status': 'paid'}, {'name': 'Amy', 'dept': 'eng', 'amount': 70, 'status': 'pending'}, {'name': 'Mia', 'dept': 'eng', 'amount': 70, 'status': 'paid'}], 'REPORT\n== Eng ==\n  rows: 3  paid: 140.00  pending: 70.00\n  top: Amy (70.00)\nTOTAL paid: 140.00  pending: 70.00'),
    ('tie_later_bigger', [{'name': 'Zed', 'dept': 'eng', 'amount': 10, 'status': 'paid'}, {'name': 'Amy', 'dept': 'eng', 'amount': 70, 'status': 'paid'}, {'name': 'Bob', 'dept': 'eng', 'amount': 70, 'status': 'paid'}], 'REPORT\n== Eng ==\n  rows: 3  paid: 150.00  pending: 0.00\n  top: Amy (70.00)\nTOTAL paid: 150.00  pending: 0.00'),
    ('void_ignored', [{'name': 'Ana', 'dept': 'eng', 'amount': 100, 'status': 'void'}, {'name': 'Bo', 'dept': 'eng', 'amount': 5, 'status': 'paid'}], 'REPORT\n== Eng ==\n  rows: 1  paid: 5.00  pending: 0.00\n  top: Bo (5.00)\nTOTAL paid: 5.00  pending: 0.00'),
    ('only_void', [{'name': 'Ana', 'dept': 'eng', 'amount': 100, 'status': 'void'}], 'REPORT\nno data'),
    ('bad_amounts', [{'name': 'Ana', 'dept': 'eng', 'amount': -5, 'status': 'paid'}, {'name': 'Bo', 'dept': 'eng', 'amount': '12', 'status': 'paid'}, {'name': 'Cy', 'dept': 'eng', 'amount': True, 'status': 'paid'}, {'name': 'Di', 'dept': 'eng', 'amount': None, 'status': 'paid'}, {'name': 'Ed', 'dept': 'eng', 'amount': 10, 'status': 'paid'}], 'REPORT\n== Eng ==\n  rows: 1  paid: 10.00  pending: 0.00\n  top: Ed (10.00)\nTOTAL paid: 10.00  pending: 0.00\nSKIPPED: 4'),
    ('bad_names_depts', [{'name': '', 'dept': 'eng', 'amount': 5, 'status': 'paid'}, {'name': '  ', 'dept': 'eng', 'amount': 5, 'status': 'paid'}, {'dept': 'eng', 'amount': 5, 'status': 'paid'}, {'name': 'Fay', 'dept': '', 'amount': 5, 'status': 'paid'}, {'name': 'Gus', 'dept': '   ', 'amount': 5, 'status': 'paid'}, {'name': 'Hal', 'dept': None, 'amount': 5, 'status': 'paid'}], 'REPORT\nno data\nSKIPPED: 6'),
    ('bad_status', [{'name': 'Ana', 'dept': 'eng', 'amount': 5, 'status': 'refunded'}, {'name': 'Bo', 'dept': 'eng', 'amount': 5}, {'name': 'Cy', 'dept': 'eng', 'amount': 7, 'status': 'paid'}], 'REPORT\n== Eng ==\n  rows: 1  paid: 7.00  pending: 0.00\n  top: Cy (7.00)\nTOTAL paid: 7.00  pending: 0.00\nSKIPPED: 2'),
    ('all_skipped', [{'name': '', 'dept': 'eng', 'amount': 5, 'status': 'paid'}, {'name': 'Ana', 'dept': 'eng', 'amount': -1, 'status': 'paid'}], 'REPORT\nno data\nSKIPPED: 2'),
    ('dept_normalised', [{'name': 'Ana', 'dept': ' ENG ', 'amount': 10, 'status': 'paid'}, {'name': 'Bo', 'dept': 'eng', 'amount': 20, 'status': 'paid'}, {'name': 'Cy', 'dept': 'Eng', 'amount': 30, 'status': 'pending'}, {'name': 'Di', 'dept': 'data science', 'amount': 1, 'status': 'paid'}], 'REPORT\n== Data Science ==\n  rows: 1  paid: 1.00  pending: 0.00\n  top: Di (1.00)\n== Eng ==\n  rows: 3  paid: 30.00  pending: 30.00\n  top: Cy (30.00)\nTOTAL paid: 31.00  pending: 30.00'),
    ('names_stripped', [{'name': '  Ana  ', 'dept': 'eng', 'amount': 9.99, 'status': 'paid'}], 'REPORT\n== Eng ==\n  rows: 1  paid: 9.99  pending: 0.00\n  top: Ana (9.99)\nTOTAL paid: 9.99  pending: 0.00'),
    ('zero_amount', [{'name': 'Ana', 'dept': 'eng', 'amount': 0, 'status': 'paid'}, {'name': 'Bo', 'dept': 'eng', 'amount': 0, 'status': 'pending'}], 'REPORT\n== Eng ==\n  rows: 2  paid: 0.00  pending: 0.00\n  top: Ana (0.00)\nTOTAL paid: 0.00  pending: 0.00'),
    ('float_sums', [{'name': 'A', 'dept': 'x', 'amount': 0.1, 'status': 'paid'}, {'name': 'B', 'dept': 'x', 'amount': 0.2, 'status': 'paid'}, {'name': 'C', 'dept': 'x', 'amount': 0.25, 'status': 'pending'}], 'REPORT\n== X ==\n  rows: 3  paid: 0.30  pending: 0.25\n  top: C (0.25)\nTOTAL paid: 0.30  pending: 0.25'),
    ('many', [{'name': 'n01', 'dept': 'eng', 'amount': 7.5, 'status': 'pending'}, {'name': 'n02', 'dept': 'ops', 'amount': 15.0, 'status': 'paid'}, {'name': 'n03', 'dept': 'hr', 'amount': 22.5, 'status': 'paid'}, {'name': 'n04', 'dept': 'eng', 'amount': 30.0, 'status': 'paid'}, {'name': 'n05', 'dept': 'ops', 'amount': 37.5, 'status': 'void'}, {'name': 'n06', 'dept': 'hr', 'amount': 45.0, 'status': 'paid'}, {'name': 'n07', 'dept': 'eng', 'amount': 52.5, 'status': 'pending'}, {'name': 'n08', 'dept': 'ops', 'amount': 60.0, 'status': 'paid'}, {'name': 'n09', 'dept': 'hr', 'amount': 67.5, 'status': 'paid'}, {'name': 'n10', 'dept': 'eng', 'amount': 75.0, 'status': 'paid'}, {'name': 'n11', 'dept': 'ops', 'amount': 82.5, 'status': 'void'}, {'name': 'n12', 'dept': 'hr', 'amount': 90.0, 'status': 'paid'}, {'name': 'n13', 'dept': 'eng', 'amount': 97.5, 'status': 'pending'}], 'REPORT\n== Eng ==\n  rows: 5  paid: 105.00  pending: 157.50\n  top: n13 (97.50)\n== Hr ==\n  rows: 4  paid: 225.00  pending: 0.00\n  top: n12 (90.00)\n== Ops ==\n  rows: 2  paid: 75.00  pending: 0.00\n  top: n08 (60.00)\nTOTAL paid: 405.00  pending: 157.50'),
]

MAX_FUNCTION_LINES = 15
MAX_NESTING = 3
MIN_FUNCTIONS = 4


@pytest.mark.parametrize("name,rows,expected", CASES, ids=[c[0] for c in CASES])
def test_golden_table(name, rows, expected):
    got = legacy_report([dict(r) for r in rows])
    assert got == expected, (
        f"Case {name!r}: the report changed.\n--- expected ---\n{expected}\n--- got ---\n{got}\n"
        "A refactor must not change a single character. Re-read the legacy rules (void rows, skipped rows, ties, rounding)."
    )


def test_input_rows_are_not_modified():
    rows = [{"name": " Ana ", "dept": " eng ", "amount": 5, "status": "paid"}]
    before = [dict(r) for r in rows]
    legacy_report(rows)
    assert rows == before, "legacy_report must not change the rows it is given."


def test_same_input_twice_gives_same_output():
    rows = CASES[3][1]
    assert legacy_report(rows) == legacy_report(rows), "Same input must give the same report (no state kept between calls)."


# ---- structure ----------------------------------------------------------------

def _functions():
    tree = ast.parse(Path(solution.__file__).read_text())
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _depth(node):
    nested = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncFor, ast.AsyncWith, ast.Match)
    best = 0
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef):
            continue
        extra = 1 if isinstance(child, nested) else 0
        best = max(best, extra + _depth(child))
    return best


def test_every_function_is_short():
    for fn in _functions():
        size = fn.end_lineno - fn.lineno + 1
        assert size <= MAX_FUNCTION_LINES, (
            f"{fn.name} is {size} lines (limit {MAX_FUNCTION_LINES}, counting def and docstring). "
            "Extract the inner part into a helper with a name that says what it does."
        )


def test_nesting_is_shallow():
    for fn in _functions():
        depth = _depth(fn)
        assert depth <= MAX_NESTING, (
            f"{fn.name} nests if/for/while/try {depth} levels deep (limit {MAX_NESTING}). "
            "Use early 'continue'/'return' for the bad cases and move inner blocks to helper functions."
        )


def test_split_into_several_functions():
    count = len(_functions())
    assert count >= MIN_FUNCTIONS, (
        f"Only {count} function(s). Split the work (check a row, update the totals, format a department, ...) "
        f"into at least {MIN_FUNCTIONS}."
    )
    assert "legacy_report" in {fn.name for fn in _functions()}, "Keep the public function legacy_report(rows)."
