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

CORRECT = 'def fetch_with_retry(client, url, attempts=3):\n    """Call client.get(url). Retry on ConnectionError: at most `attempts` calls in total.\n    Other exceptions are not retried. After the last failure raise the last ConnectionError.\n    attempts < 1 raises ValueError."""\n    if attempts < 1:\n        raise ValueError("attempts must be at least 1")\n    last = None\n    for _ in range(attempts):\n        try:\n            return client.get(url)\n        except ConnectionError as error:\n            last = error\n    raise last'

MUTANTS = {'one_attempt_short': ('def fetch_with_retry(client, url, attempts=3):\n    if attempts < 1:\n        raise ValueError("attempts must be at least 1")\n    last = None\n    for _ in range(attempts - 1):\n        try:\n            return client.get(url)\n        except ConnectionError as error:\n            last = error\n    raise last', 'only attempts-1 calls are made, so success on the last allowed attempt is missed.'), 'one_attempt_extra': ('def fetch_with_retry(client, url, attempts=3):\n    if attempts < 1:\n        raise ValueError("attempts must be at least 1")\n    last = None\n    for _ in range(attempts + 1):\n        try:\n            return client.get(url)\n        except ConnectionError as error:\n            last = error\n    raise last', 'one call too many is made after the allowed attempts are used up.'), 'retries_every_error': ('def fetch_with_retry(client, url, attempts=3):\n    if attempts < 1:\n        raise ValueError("attempts must be at least 1")\n    last = None\n    for _ in range(attempts):\n        try:\n            return client.get(url)\n        except Exception as error:\n            last = error\n    raise last', 'errors other than ConnectionError (for example ValueError) are retried and then re-raised after all attempts.'), 'no_retry': ('def fetch_with_retry(client, url, attempts=3):\n    if attempts < 1:\n        raise ValueError("attempts must be at least 1")\n    return client.get(url)', 'the call is never retried.'), 'swallows_failure': ('def fetch_with_retry(client, url, attempts=3):\n    if attempts < 1:\n        raise ValueError("attempts must be at least 1")\n    for _ in range(attempts):\n        try:\n            return client.get(url)\n        except ConnectionError:\n            pass\n    return None', 'after the last failure None is returned instead of raising ConnectionError.'), 'raises_first_error': ('def fetch_with_retry(client, url, attempts=3):\n    if attempts < 1:\n        raise ValueError("attempts must be at least 1")\n    first = None\n    for _ in range(attempts):\n        try:\n            return client.get(url)\n        except ConnectionError as error:\n            if first is None:\n                first = error\n    raise first', 'the FIRST ConnectionError is raised instead of the last one.'), 'attempts_ignored': ('def fetch_with_retry(client, url, attempts=3):\n    if attempts < 1:\n        raise ValueError("attempts must be at least 1")\n    last = None\n    for _ in range(3):\n        try:\n            return client.get(url)\n        except ConnectionError as error:\n            last = error\n    raise last', 'the attempts argument is ignored (always 3 calls).'), 'no_validation': ('def fetch_with_retry(client, url, attempts=3):\n    last = None\n    for _ in range(attempts):\n        try:\n            return client.get(url)\n        except ConnectionError as error:\n            last = error\n    raise last', 'attempts=0 does not raise ValueError.')}

MIN_TESTS = 5


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


def test_catches_one_attempt_short():
    caught('one_attempt_short')

def test_catches_one_attempt_extra():
    caught('one_attempt_extra')

def test_catches_retries_every_error():
    caught('retries_every_error')

def test_catches_no_retry():
    caught('no_retry')

def test_catches_swallows_failure():
    caught('swallows_failure')

def test_catches_raises_first_error():
    caught('raises_first_error')

def test_catches_attempts_ignored():
    caught('attempts_ignored')

def test_catches_no_validation():
    caught('no_validation')


def test_requirement_side_effect():
    assert "side_effect" in LEARNER_SOURCE, "Use Mock.side_effect to script failures and results."
    assert "call_count" in LEARNER_SOURCE or "assert_called" in LEARNER_SOURCE, (
        "Check how many times client.get was called (call_count or assert_called_with...).")
