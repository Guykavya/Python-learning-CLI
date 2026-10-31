import ast
import os
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called target.py that holds the code under test, and real pytest runs on it.
# First against the CORRECT target (all your tests must pass), then against several BUGGY
# targets (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()

CORRECT = 'import csv\n\n\ndef summarise(path):\n    """Read a CSV file with the header \'category,amount\' and return {category: total}.\n    Categories are stripped and lower-cased. Rows with a blank amount are skipped.\n    Totals are rounded to 2 decimals. A missing file raises FileNotFoundError."""\n    totals = {}\n    with open(path, newline="") as handle:\n        for row in csv.DictReader(handle):\n            amount = row["amount"].strip()\n            if not amount:\n                continue\n            category = row["category"].strip().lower()\n            totals[category] = round(totals.get(category, 0) + float(amount), 2)\n    return totals'

MUTANTS = {'case_sensitive': ('import csv\n\n\ndef summarise(path):\n    totals = {}\n    with open(path, newline="") as handle:\n        for row in csv.DictReader(handle):\n            amount = row["amount"].strip()\n            if not amount:\n                continue\n            category = row["category"].strip()\n            totals[category] = round(totals.get(category, 0) + float(amount), 2)\n    return totals', "categories are not lower-cased, so 'Food' and 'food' are counted apart."), 'no_strip': ('import csv\n\n\ndef summarise(path):\n    totals = {}\n    with open(path, newline="") as handle:\n        for row in csv.DictReader(handle):\n            amount = row["amount"].strip()\n            if not amount:\n                continue\n            category = row["category"].lower()\n            totals[category] = round(totals.get(category, 0) + float(amount), 2)\n    return totals', "spaces around a category are not stripped, so ' food' and 'food' are counted apart."), 'overwrites': ('import csv\n\n\ndef summarise(path):\n    totals = {}\n    with open(path, newline="") as handle:\n        for row in csv.DictReader(handle):\n            amount = row["amount"].strip()\n            if not amount:\n                continue\n            category = row["category"].strip().lower()\n            totals[category] = round(float(amount), 2)\n    return totals', 'a second row of the same category replaces the total instead of adding to it.'), 'counts_rows': ('import csv\n\n\ndef summarise(path):\n    totals = {}\n    with open(path, newline="") as handle:\n        for row in csv.DictReader(handle):\n            amount = row["amount"].strip()\n            if not amount:\n                continue\n            category = row["category"].strip().lower()\n            totals[category] = totals.get(category, 0) + 1\n    return totals', 'the number of rows is returned instead of the sum of the amounts.'), 'blank_not_skipped': ('import csv\n\n\ndef summarise(path):\n    totals = {}\n    with open(path, newline="") as handle:\n        for row in csv.DictReader(handle):\n            amount = row["amount"].strip()\n            amount = amount or "0"\n            category = row["category"].strip().lower()\n            totals[category] = round(totals.get(category, 0) + float(amount), 2)\n    return totals', 'a blank amount is not skipped (it is treated as 0, so the category appears with 0 or crashes).'), 'zero_skipped': ('import csv\n\n\ndef summarise(path):\n    totals = {}\n    with open(path, newline="") as handle:\n        for row in csv.DictReader(handle):\n            amount = row["amount"].strip()\n            if not amount or float(amount) == 0:\n                continue\n            category = row["category"].strip().lower()\n            totals[category] = round(totals.get(category, 0) + float(amount), 2)\n    return totals', 'rows with amount 0 are dropped, so a category that only has 0 amounts disappears.'), 'missing_file_ignored': ('import csv\n\n\ndef summarise(path):\n    totals = {}\n    try:\n        handle = open(path, newline="")\n    except FileNotFoundError:\n        return totals\n    with handle:\n        for row in csv.DictReader(handle):\n            amount = row["amount"].strip()\n            if not amount:\n                continue\n            category = row["category"].strip().lower()\n            totals[category] = round(totals.get(category, 0) + float(amount), 2)\n    return totals', 'a missing file returns {} instead of raising FileNotFoundError.'), 'no_rounding': ('import csv\n\n\ndef summarise(path):\n    totals = {}\n    with open(path, newline="") as handle:\n        for row in csv.DictReader(handle):\n            amount = row["amount"].strip()\n            if not amount:\n                continue\n            category = row["category"].strip().lower()\n            totals[category] = totals.get(category, 0) + float(amount)\n    return totals', 'totals are not rounded: 0.1 + 0.2 gives 0.30000000000000004.')}

MIN_TESTS = 3


@lru_cache(maxsize=None)
def run_suite(target_source):
    with tempfile.TemporaryDirectory(prefix="learn-mut-") as tmp:
        tmp = Path(tmp)
        (tmp / "target.py").write_text(target_source)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_learner.py", "-q", "--no-header",
                 "-p", "no:cacheprovider", "--tb=short"],
                cwd=tmp, capture_output=True, text=True, timeout=60, env=env)
        except subprocess.TimeoutExpired:
            return 124, "pytest timed out (infinite loop in a test?)"
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), ".")


def test_tests_pass_on_the_correct_code():
    code, out = run_suite(CORRECT)
    assert code != 5, ("No tests were collected. Write functions whose names start with test_ "
                       "in solution.py.")
    assert code == 0, ("Your tests must PASS on the correct code, but they failed or crashed. "
                       "A wrong expected value or a wrong mock setup is the usual cause. pytest said:\n"
                       + out[-1800:])


def test_you_wrote_enough_tests():
    tree = ast.parse(LEARNER_SOURCE)
    names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    assert len(names) >= MIN_TESTS, (
        f"Write at least {MIN_TESTS} test functions (names starting with test_); you have {len(names)}.")
    assert len(names) == len(set(names)), (
        "Two test functions share a name. The second silently replaces the first, so only one runs.")


def caught(name):
    source, why = MUTANTS[name]
    code, out = run_suite(source)
    assert code == 1, (
        f"Your tests did NOT catch this bug: {why} "
        "Add a test whose expected value differs between the correct code and the buggy one."
        + ("" if code == 0 else f" (pytest exit code {code}; output: {out[-300:]})"))


def test_catches_case_sensitive():
    caught('case_sensitive')

def test_catches_no_strip():
    caught('no_strip')

def test_catches_overwrites():
    caught('overwrites')

def test_catches_counts_rows():
    caught('counts_rows')

def test_catches_blank_not_skipped():
    caught('blank_not_skipped')

def test_catches_zero_skipped():
    caught('zero_skipped')

def test_catches_missing_file_ignored():
    caught('missing_file_ignored')

def test_catches_no_rounding():
    caught('no_rounding')


def test_requirement_tmp_path_and_parametrize():
    assert "tmp_path" in LEARNER_SOURCE, "Write the CSV files into the tmp_path fixture, never into a fixed folder."
    assert "parametrize" in LEARNER_SOURCE or "fixture" in LEARNER_SOURCE, (
        "Use @pytest.mark.parametrize (or a fixture) so one test body covers several CSV contents.")
