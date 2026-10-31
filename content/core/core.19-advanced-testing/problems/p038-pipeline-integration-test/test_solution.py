import ast
import os
import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called pipeline.py that holds the code under test, and real pytest runs on it.
# First against the CORRECT code (all your tests must pass), then against several BUGGY
# copies (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()

MODULE = "pipeline"
MIN_TESTS = 5
HYPOTHESIS = False

CORRECT = r'''import csv


def read_rows(path):
    """Read a CSV file with the header date,category,amount. Return a list of dicts of strings."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clean(rows):
    """Tidy the rows. Category: strip spaces, lower-case. Amount: text -> float.

    Drop a row when its amount is blank, not a number, or negative (refunds are ignored).
    """
    cleaned = []
    for row in rows:
        category = row["category"].strip().lower()
        try:
            amount = float(row["amount"])
        except ValueError:
            continue
        if amount < 0:
            continue
        cleaned.append({"category": category, "amount": amount})
    return cleaned


def aggregate(rows):
    """Return {category: (total, count)} for cleaned rows."""
    totals = {}
    for row in rows:
        total, count = totals.get(row["category"], (0.0, 0))
        totals[row["category"]] = (total + row["amount"], count + 1)
    return totals


def write_report(summary, path):
    """Write category,total,count lines: biggest total first, ties by category name.

    Totals have 2 decimals. The header line is always written. Return the number of data lines.
    """
    ordered = sorted(summary.items(), key=lambda item: (-item[1][0], item[0]))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "total", "count"])
        for category, (total, count) in ordered:
            writer.writerow([category, f"{total:.2f}", count])
    return len(ordered)


def run(src, dst):
    """The whole pipeline: read src, clean, aggregate, write dst. Return the number of report lines."""
    return write_report(aggregate(clean(read_rows(src))), dst)'''

# name -> (text to replace in CORRECT, replacement, what the bug does)
MUTANTS = {'keeps_blank_amounts': ('        try:\n'
                         '            amount = float(row["amount"])\n'
                         '        except ValueError:\n'
                         '            continue\n',
                         '        amount = float(row["amount"] or 0)\n',
                         'a row with a blank amount is counted as 0 instead of being dropped (and a text '
                         'amount crashes).'),
 'case_not_merged': ('category = row["category"].strip().lower()',
                     'category = row["category"].strip()',
                     "'Food' and 'food' are counted as two categories."),
 'spaces_not_stripped': ('category = row["category"].strip().lower()',
                         'category = row["category"].lower()',
                         "' food' and 'food' are counted as two categories."),
 'refunds_kept': ('        if amount < 0:\n            continue\n',
                  '',
                  'negative amounts (refunds) are added to the totals instead of being dropped.'),
 'sorted_by_name': ('key=lambda item: (-item[1][0], item[0])',
                    'key=lambda item: item[0]',
                    'the report is ordered by category name, not by biggest total first.'),
 'ties_in_input_order': ('key=lambda item: (-item[1][0], item[0])',
                         'key=lambda item: -item[1][0]',
                         'categories with equal totals appear in input order instead of alphabetical order.'),
 'no_header': ('        writer.writerow(["category", "total", "count"])\n',
               '',
               'the header line is missing from the report.'),
 'total_not_rounded': ('f"{total:.2f}"',
                       'total',
                       'totals are written as raw floats (10.5 instead of 10.50).'),
 'run_skips_clean': ('return write_report(aggregate(clean(read_rows(src))), dst)',
                     'return write_report(aggregate([{"category": r["category"], "amount": float(r["amount"] '
                     'or 0)} for r in read_rows(src)]), dst)',
                     'run does not call clean: every unit works, but the glue skips a step (categories are '
                     'not tidied, refunds are kept).'),
 'run_returns_input_count': ('return write_report(aggregate(clean(read_rows(src))), dst)',
                             'rows = read_rows(src)\n'
                             '    write_report(aggregate(clean(rows)), dst)\n'
                             '    return len(rows)',
                             'run returns the number of input rows instead of the number of report lines.')}

# Makes hypothesis deterministic and quiet inside the temporary folder, whatever you wrote.
CONFTEST = """
from hypothesis import settings
settings.register_profile("learn", settings(derandomize=True, database=None, max_examples=100, deadline=None))
settings.load_profile("learn")
"""


def mutate(name):
    old, new, _why = MUTANTS[name]
    assert CORRECT.count(old) == 1, f"author error: snippet of {name} is not unique"
    return CORRECT.replace(old, new)


@lru_cache(maxsize=None)
def run_suite(target_source):
    with tempfile.TemporaryDirectory(prefix="learn-mut-") as tmp:
        tmp = Path(tmp)
        (tmp / (MODULE + ".py")).write_text(target_source)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        (tmp / "conftest.py").write_text(CONFTEST)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_learner.py", "-q", "--no-header",
                 "-p", "no:cacheprovider", "--tb=short"],
                cwd=tmp, capture_output=True, text=True, timeout=90, env=env)
        except subprocess.TimeoutExpired:
            return 124, "pytest timed out (infinite loop or a test that is far too slow?)"
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), ".")


def test_tests_pass_on_the_correct_code():
    code, out = run_suite(CORRECT)
    assert code != 5, ("No tests were collected. Write functions whose names start with test_ "
                       "in solution.py.")
    assert code == 0, ("Your tests must PASS on the correct code, but they failed or crashed. "
                       "A wrong expected value or a wrong property is the usual cause. pytest said:\n"
                       + out[-1800:])


def test_you_wrote_enough_tests():
    tree = ast.parse(LEARNER_SOURCE)
    names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    assert len(names) >= MIN_TESTS, (
        f"Write at least {MIN_TESTS} test functions (names starting with test_); you have {len(names)}.")
    assert len(names) == len(set(names)), (
        "Two test functions share a name. The second silently replaces the first, so only one runs.")


def test_hypothesis_is_deterministic():
    if not HYPOTHESIS:
        return
    assert "given" in LEARNER_SOURCE, "Use hypothesis: import given and strategies, then decorate with @given(...)."
    assert "derandomize=True" in LEARNER_SOURCE and "database=None" in LEARNER_SOURCE, (
        "Put @settings(derandomize=True, database=None, max_examples=100) above every @given test. "
        "Derandomize makes the run repeatable and database=None stops hypothesis writing a .hypothesis folder.")
    for number in re.findall(r"max_examples\s*=\s*(\d+)", LEARNER_SOURCE):
        assert int(number) <= 100, "Keep max_examples at 100 or less so the checker stays fast."


def caught(name):
    _old, _new, why = MUTANTS[name]
    code, out = run_suite(mutate(name))
    assert code == 1, (
        f"Your tests did NOT catch the bug '{name}': {why} "
        "Add a test whose result differs between the correct code and the buggy one."
        + ("" if code == 0 else f" (pytest exit code {code}; output: {out[-300:]})"))

def test_catches_keeps_blank_amounts():
    caught('keeps_blank_amounts')

def test_catches_case_not_merged():
    caught('case_not_merged')

def test_catches_spaces_not_stripped():
    caught('spaces_not_stripped')

def test_catches_refunds_kept():
    caught('refunds_kept')

def test_catches_sorted_by_name():
    caught('sorted_by_name')

def test_catches_ties_in_input_order():
    caught('ties_in_input_order')

def test_catches_no_header():
    caught('no_header')

def test_catches_total_not_rounded():
    caught('total_not_rounded')

def test_catches_run_skips_clean():
    caught('run_skips_clean')

def test_catches_run_returns_input_count():
    caught('run_returns_input_count')


def test_you_use_tmp_path_and_run():
    assert "tmp_path" in LEARNER_SOURCE, "Use the tmp_path fixture: real files, in a throw-away folder."
    assert "run(" in LEARNER_SOURCE, "An integration test calls the whole pipeline, run(src, dst), not only the pieces."
