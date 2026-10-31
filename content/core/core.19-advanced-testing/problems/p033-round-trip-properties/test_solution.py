import ast
import os
import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called target.py that holds the code under test, and real pytest runs on it.
# First against the CORRECT code (all your tests must pass), then against several BUGGY
# copies (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()

MODULE = "target"
MIN_TESTS = 3
HYPOTHESIS = True

CORRECT = r'''def encode(text):
    """Run-length encode letters: "aaabcc" -> "a3b1c2". Every run is written, even a run of 1.

    Only letters are allowed (anything else raises ValueError).
    """
    if not text.isalpha() and text != "":
        raise ValueError("letters only")
    out = []
    i = 0
    while i < len(text):
        j = i
        while j < len(text) and text[j] == text[i]:
            j += 1
        out.append(text[i] + str(j - i))
        i = j
    return "".join(out)


def decode(code):
    """Undo encode: "a3b1c2" -> "aaabcc". The count after a letter can have several digits."""
    out = []
    i = 0
    while i < len(code):
        letter = code[i]
        j = i + 1
        while j < len(code) and code[j].isdigit():
            j += 1
        out.append(letter * int(code[i + 1:j]))
        i = j
    return "".join(out)'''

# name -> (text to replace in CORRECT, replacement, what the bug does)
MUTANTS = {'decode_one_digit_counts': ('while j < len(code) and code[j].isdigit():\n'
                             '            j += 1\n'
                             '        out.append(letter * int(code[i + 1:j]))',
                             'j = i + 2\n        out.append(letter * int(code[i + 1:j]))',
                             'decode reads only one digit of the count, so a run of 12 letters comes back as '
                             '1 letter followed by junk.'),
 'encode_merges_far_runs': ('out = []\n'
                            '    i = 0\n'
                            '    while i < len(text):\n'
                            '        j = i\n'
                            '        while j < len(text) and text[j] == text[i]:\n'
                            '            j += 1\n'
                            '        out.append(text[i] + str(j - i))\n'
                            '        i = j\n'
                            '    return "".join(out)',
                            'return "".join(c + str(text.count(c)) for c in dict.fromkeys(text))',
                            "encode counts every letter in the whole text, so 'aba' becomes 'a2b1' and "
                            "decodes to 'aab'."),
 'encode_drops_last_run': ('        out.append(text[i] + str(j - i))\n        i = j\n    return "".join(out)',
                           '        if j < len(text):\n'
                           '            out.append(text[i] + str(j - i))\n'
                           '        i = j\n'
                           '    return "".join(out)',
                           "encode forgets the final run, so 'ab' becomes 'a1'."),
 'encode_splits_at_9': ('out.append(text[i] + str(j - i))',
                        'n = j - i\n'
                        '        while n > 9:\n'
                        '            out.append(text[i] + "9")\n'
                        '            n -= 9\n'
                        '        out.append(text[i] + str(n))',
                        "a run longer than 9 is written as several pieces ('a9a3' instead of 'a12'). It "
                        'still decodes back correctly, so only a test of the encoded text can see it.'),
 'decode_empty_crashes': ('    out = []\n    i = 0\n    while i < len(code):\n        letter = code[i]',
                          '    out = []\n'
                          '    i = 0\n'
                          '    letter = code[0]\n'
                          '    while i < len(code):\n'
                          '        letter = code[i]',
                          "decode('') raises IndexError instead of returning ''."),
 'encode_accepts_digits': ('    if not text.isalpha() and text != "":\n'
                           '        raise ValueError("letters only")\n',
                           '',
                           "encode('a1') is accepted instead of raising ValueError, and the code 'a111' "
                           'cannot be decoded back.')}

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

def test_catches_decode_one_digit_counts():
    caught('decode_one_digit_counts')

def test_catches_encode_merges_far_runs():
    caught('encode_merges_far_runs')

def test_catches_encode_drops_last_run():
    caught('encode_drops_last_run')

def test_catches_encode_splits_at_9():
    caught('encode_splits_at_9')

def test_catches_decode_empty_crashes():
    caught('decode_empty_crashes')

def test_catches_encode_accepts_digits():
    caught('encode_accepts_digits')
