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
MIN_TESTS = 5
HYPOTHESIS = True

CORRECT = r'''def normalise_whitespace(text):
    """Collapse every run of whitespace (spaces, tabs, newlines) into one space and strip both ends."""
    return " ".join(text.split())


def dedupe(items):
    """Remove repeated items. Keep the FIRST occurrence of each and the original order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def sort_by_length(words):
    """Return a new list ordered by length, shortest first. Words of equal length keep their original order."""
    return sorted(words, key=len)'''

# name -> (text to replace in CORRECT, replacement, what the bug does)
MUTANTS = {'keeps_tabs_and_newlines': ('return " ".join(text.split())',
                             'return " ".join(text.split(" ")).strip(" ")',
                             'only plain spaces are treated as separators: tabs and newlines survive, and '
                             'runs of spaces leave empty pieces.'),
 'no_strip': ('return " ".join(text.split())',
              'import re\n    return re.sub(r"\\s+", " ", text)',
              'runs are collapsed but a leading or trailing space is left in place.'),
 'only_halves_runs': ('return " ".join(text.split())',
                      'return text.strip().replace("  ", " ")',
                      'each pair of spaces becomes one space, so a run of four becomes two: the result is '
                      'not stable when normalised again.'),
 'changes_the_words': ('return " ".join(text.split())',
                       'return " ".join(text.split()).lower()',
                       'the words themselves are changed (lower-cased), not just the spacing.'),
 'dedupe_sorts': ('    seen = set()\n'
                  '    result = []\n'
                  '    for item in items:\n'
                  '        if item not in seen:\n'
                  '            seen.add(item)\n'
                  '            result.append(item)\n'
                  '    return result',
                  '    return sorted(set(items))',
                  'dedupe returns the items in sorted order instead of first-occurrence order.'),
 'dedupe_keeps_last': ('        if item not in seen:\n'
                       '            seen.add(item)\n'
                       '            result.append(item)',
                       '        if item in seen:\n'
                       '            result.remove(item)\n'
                       '        seen.add(item)\n'
                       '        result.append(item)',
                       'dedupe keeps the last occurrence of an item, so the order of the survivors changes.'),
 'dedupe_drops_zero': ('        if item not in seen:',
                       '        if item and item not in seen:',
                       'falsy items (0, empty string) are thrown away.'),
 'sort_not_stable': ('return sorted(words, key=len)',
                     'return sorted(words, key=lambda w: (len(w), w))',
                     'words of the same length are sorted alphabetically instead of keeping their original '
                     'order.'),
 'sort_longest_first': ('return sorted(words, key=len)',
                        'return sorted(words, key=len, reverse=True)',
                        'the longest words come first.')}

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

def test_catches_keeps_tabs_and_newlines():
    caught('keeps_tabs_and_newlines')

def test_catches_no_strip():
    caught('no_strip')

def test_catches_only_halves_runs():
    caught('only_halves_runs')

def test_catches_changes_the_words():
    caught('changes_the_words')

def test_catches_dedupe_sorts():
    caught('dedupe_sorts')

def test_catches_dedupe_keeps_last():
    caught('dedupe_keeps_last')

def test_catches_dedupe_drops_zero():
    caught('dedupe_drops_zero')

def test_catches_sort_not_stable():
    caught('sort_not_stable')

def test_catches_sort_longest_first():
    caught('sort_longest_first')
