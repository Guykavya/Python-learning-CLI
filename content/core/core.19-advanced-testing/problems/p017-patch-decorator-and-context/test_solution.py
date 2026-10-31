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

CORRECT = 'import os\nimport shutil\n\n\ndef backup(path):\n    """Copy the file to path + \'.bak\' and return the new path. Missing file: FileNotFoundError."""\n    if not os.path.exists(path):\n        raise FileNotFoundError(path)\n    destination = path + ".bak"\n    shutil.copy(path, destination)\n    return destination'

MUTANTS = {'no_exists_check': ('import os\nimport shutil\n\n\ndef backup(path):\n    destination = path + ".bak"\n    shutil.copy(path, destination)\n    return destination', 'a missing file does not raise FileNotFoundError.'), 'wrong_suffix': ('import os\nimport shutil\n\n\ndef backup(path):\n    if not os.path.exists(path):\n        raise FileNotFoundError(path)\n    destination = path + ".backup"\n    shutil.copy(path, destination)\n    return destination', "the copy is named path + '.backup' instead of path + '.bak'."), 'args_swapped': ('import os\nimport shutil\n\n\ndef backup(path):\n    if not os.path.exists(path):\n        raise FileNotFoundError(path)\n    destination = path + ".bak"\n    shutil.copy(destination, path)\n    return destination', 'shutil.copy gets (destination, source): the backup would overwrite the original.'), 'returns_original': ('import os\nimport shutil\n\n\ndef backup(path):\n    if not os.path.exists(path):\n        raise FileNotFoundError(path)\n    destination = path + ".bak"\n    shutil.copy(path, destination)\n    return path', 'the original path is returned instead of the backup path.'), 'copies_before_checking': ('import os\nimport shutil\n\n\ndef backup(path):\n    destination = path + ".bak"\n    shutil.copy(path, destination)\n    if not os.path.exists(path):\n        raise FileNotFoundError(path)\n    return destination', 'the copy is attempted even for a missing file (it must not be called when the file is missing).'), 'copies_twice': ('import os\nimport shutil\n\n\ndef backup(path):\n    if not os.path.exists(path):\n        raise FileNotFoundError(path)\n    destination = path + ".bak"\n    shutil.copy(path, destination)\n    shutil.copy(path, destination)\n    return destination', 'the file is copied twice.')}

MIN_TESTS = 4


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


def test_catches_no_exists_check():
    caught('no_exists_check')

def test_catches_wrong_suffix():
    caught('wrong_suffix')

def test_catches_args_swapped():
    caught('args_swapped')

def test_catches_returns_original():
    caught('returns_original')

def test_catches_copies_before_checking():
    caught('copies_before_checking')

def test_catches_copies_twice():
    caught('copies_twice')


def _patch_names(tree):
    """Return (decorator_uses, with_uses): how often patch is used as decorator / context manager."""
    def is_patch_call(node):
        if not isinstance(node, ast.Call):
            return False
        f = node.func
        while isinstance(f, ast.Attribute) and f.attr != "patch":
            f = f.value
        return (isinstance(f, ast.Name) and f.id == "patch") or (isinstance(f, ast.Attribute) and f.attr == "patch")
    deco = with_ = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            deco += sum(is_patch_call(d) for d in node.decorator_list)
        if isinstance(node, ast.With):
            with_ += sum(is_patch_call(i.context_expr) for i in node.items)
    return deco, with_


def test_requirement_patch_both_ways():
    deco, with_ = _patch_names(ast.parse(LEARNER_SOURCE))
    assert deco >= 1, "Use patch as a DECORATOR (@patch('target....')) in at least one test."
    assert with_ >= 1, "Use patch as a CONTEXT MANAGER (with patch('target....') as m:) in at least one test."
