import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to target.py
# (the function from problem.md) and run by real pytest with coverage.py measuring target.py with
# BRANCH coverage switched on. First on the correct code: all your tests must pass AND every line and
# every branch (every way an "if" or a loop can go) must have been run. Then on buggy copies:
# at least one of your tests must fail on each, so your tests must really assert something.

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()
MIN_TESTS = 5

CORRECT = r'''def parcel_fee(weight, zone, express, coupons):
    """Fee in cents for a parcel.

    Base 500. Over 20 kg add 1500; over 5 kg (up to 20) add 500. Zone "abroad" multiplies by 3
    and does not allow express (ValueError); at home, express adds 1000. A weight of 0 or less is a
    ValueError. Then the coupon codes are read in order: "FREE" makes the parcel free at once,
    "HALF" halves the fee (rounded down) and ignores the codes after it. Other codes do nothing.
    """
    if weight <= 0:
        raise ValueError("weight must be positive")
    fee = 500
    if weight > 20:
        fee += 1500
    elif weight > 5:
        fee += 500
    if zone == "abroad":
        fee *= 3
        if express:
            raise ValueError("no express abroad")
    elif express:
        fee += 1000
    for code in coupons:
        if code == "FREE":
            return 0
        if code == "HALF":
            fee //= 2
            break
    return fee'''
MUTANTS = {'heavy_surcharge_wrong': ('fee += 1500',
                           'fee += 1000',
                           'parcels over 20 kg pay a surcharge of 1000 instead of 1500.'),
 'medium_surcharge_wrong': ('fee += 500', 'fee += 400', 'parcels over 5 kg pay 400 extra instead of 500.'),
 'heavy_border': ('if weight > 20:',
                  'if weight >= 20:',
                  "a parcel of exactly 20 kg is charged as heavy (the rule is 'over 20')."),
 'abroad_factor': ('fee *= 3', 'fee *= 2', 'abroad parcels pay double instead of triple.'),
 'express_at_home': ('fee += 1000', 'fee += 500', 'express at home adds 500 instead of 1000.'),
 'free_is_not_free': ('            return 0',
                      '            return fee',
                      'the FREE coupon returns the fee instead of 0.'),
 'half_is_a_third': ('fee //= 2', 'fee //= 3', 'the HALF coupon divides by 3.'),
 'half_does_not_stop': ('            fee //= 2\n            break',
                        '            fee //= 2',
                        'after HALF the later codes are still read (a later FREE still works).')}

RUNNER = """
import json, sys
from pathlib import Path
import coverage, pytest

target = str(Path("target.py").resolve())
cov = coverage.Coverage(branch=True, data_file=None, include=[target])
cov.start()
code = pytest.main(["test_learner.py", "-q", "--no-header", "-p", "no:cacheprovider", "--tb=short"])
cov.stop()
cov.json_report(outfile="cov.json")
data = json.loads(Path("cov.json").read_text())
info = list(data["files"].values())[0]
Path("result.json").write_text(json.dumps({
    "code": int(code),
    "missing_lines": info["missing_lines"],
    "missing_branches": info["missing_branches"],
}))
"""


@lru_cache(maxsize=None)
def run_suite(target_source):
    with tempfile.TemporaryDirectory(prefix="learn-cov-") as tmp:
        tmp = Path(tmp)
        (tmp / "target.py").write_text(target_source)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        (tmp / "runner.py").write_text(RUNNER)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
        try:
            proc = subprocess.run([sys.executable, "runner.py"], cwd=tmp, capture_output=True, text=True,
                                  timeout=90, env=env)
        except subprocess.TimeoutExpired:
            return {"code": 124, "output": "timed out", "missing_lines": [], "missing_branches": []}
        out = (proc.stdout + proc.stderr).replace(str(tmp), ".")
        result_file = tmp / "result.json"
        if not result_file.exists():
            return {"code": 3, "output": out, "missing_lines": [], "missing_branches": []}
        result = json.loads(result_file.read_text())
        result["output"] = out
        return result


def describe(line, to):
    text = CORRECT.splitlines()[line - 1].strip()
    if to < 0:
        return f"line {line} (`{text}`) never finished normally (never left the function from there)"
    target_text = CORRECT.splitlines()[to - 1].strip()
    return f"line {line} (`{text}`) never went on to line {to} (`{target_text}`)"


def test_tests_pass_on_the_correct_function():
    result = run_suite(CORRECT)
    assert result["code"] != 5, "No tests were collected. Write functions whose names start with test_ in solution.py."
    assert result["code"] == 0, ("Your tests must PASS on the correct function. A wrong expected value in your test is "
                                 "the usual cause. pytest said:\n" + result["output"][-1800:])


def test_you_wrote_enough_tests():
    tree = ast.parse(LEARNER_SOURCE)
    names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    assert len(names) >= MIN_TESTS, f"Write at least {MIN_TESTS} test functions; you have {len(names)}."
    assert len(names) == len(set(names)), "Two test functions share a name; the second replaces the first."


def test_every_line_is_run():
    result = run_suite(CORRECT)
    assert result["code"] == 0, "First make your tests pass on the correct function."
    lines = result["missing_lines"]
    assert not lines, ("These lines of the function never ran: "
                       + "; ".join(f"line {n} (`{CORRECT.splitlines()[n - 1].strip()}`)" for n in lines)
                       + ". Add a call that reaches them.")


def test_every_branch_is_taken_both_ways():
    result = run_suite(CORRECT)
    assert result["code"] == 0, "First make your tests pass on the correct function."
    missing = result["missing_branches"]
    assert not missing, ("Branch coverage is not complete. " + "; ".join(describe(a, b) for a, b in missing)
                         + ". For an 'if' you need one call where it is true and one where it is false; "
                         "for a loop, one call that skips it and one that runs it to the end.")


def caught(name):
    old, new, why = MUTANTS[name]
    result = run_suite(CORRECT.replace(old, new))
    assert result["code"] == 1, (
        f"Reaching a line is not checking it: your tests did NOT catch the bug '{name}': {why} "
        "Add or strengthen an assert (the exact fee) in a test that runs that line.")

def test_catches_heavy_surcharge_wrong():
    caught('heavy_surcharge_wrong')

def test_catches_medium_surcharge_wrong():
    caught('medium_surcharge_wrong')

def test_catches_heavy_border():
    caught('heavy_border')

def test_catches_abroad_factor():
    caught('abroad_factor')

def test_catches_express_at_home():
    caught('express_at_home')

def test_catches_free_is_not_free():
    caught('free_is_not_free')

def test_catches_half_is_a_third():
    caught('half_is_a_third')

def test_catches_half_does_not_stop():
    caught('half_does_not_stop')
