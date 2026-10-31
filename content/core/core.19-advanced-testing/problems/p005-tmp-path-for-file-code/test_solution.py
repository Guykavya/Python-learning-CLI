import ast
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called target.py that holds the code under test, and real pytest runs on it.
# First against the CORRECT target (all your tests must pass), then against several BUGGY
# targets (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()
TREE = ast.parse(LEARNER_SOURCE)
TESTS = [n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]


def arg_names(fn):
    return [a.arg for a in fn.args.args]


def parse_report(path):
    results = {}
    for tc in ET.parse(path).getroot().iter("testcase"):
        status = "passed"
        for child in tc:
            if child.tag in ("failure", "error"):
                status = "failed"
                break
            if child.tag == "skipped":
                status = "xfailed" if child.get("type") == "pytest.xfail" else "skipped"
        results[tc.get("name")] = status
    return results


@lru_cache(maxsize=None)
def run_suite(target_source, extra=()):
    with tempfile.TemporaryDirectory(prefix="learn-mut-") as tmp:
        tmp = Path(tmp)
        (tmp / "target.py").write_text(target_source)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_learner.py", "-q", "--no-header",
                 "-p", "no:cacheprovider", "--tb=short", "--junitxml=report.xml", *extra],
                cwd=tmp, capture_output=True, text=True, timeout=60, env=env)
        except subprocess.TimeoutExpired:
            return 124, "pytest timed out (infinite loop in a test?)", {}
        report = tmp / "report.xml"
        results = parse_report(report) if report.exists() else {}
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), "."), results

CORRECT = r'''def save_notes(path, notes):
    """Write one note per line, replacing the file. Every line ends with a newline."""
    with open(path, "w", encoding="utf-8") as f:
        for note in notes:
            f.write(note + "\n")


def load_notes(path):
    """Return the notes as a list of strings. Blank lines are skipped, a missing file gives []."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return []
    return [line for line in lines if line.strip()]'''

MUTANTS = {
    'save_appends': (r'''def save_notes(path, notes):
    """Write one note per line, replacing the file. Every line ends with a newline."""
    with open(path, "a", encoding="utf-8") as f:
        for note in notes:
            f.write(note + "\n")


def load_notes(path):
    """Return the notes as a list of strings. Blank lines are skipped, a missing file gives []."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return []
    return [line for line in lines if line.strip()]''',
        'save_notes appends to an existing file instead of replacing it (saving twice duplicates notes).'),
    'no_trailing_newline': (r'''def save_notes(path, notes):
    """Write one note per line, replacing the file. Every line ends with a newline."""
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(notes))


def load_notes(path):
    """Return the notes as a list of strings. Blank lines are skipped, a missing file gives []."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return []
    return [line for line in lines if line.strip()]''',
        "the saved text does not end with a newline, so the file is not 'one note per line, each ending in a newline'."),
    'load_missing_raises': (r'''def save_notes(path, notes):
    """Write one note per line, replacing the file. Every line ends with a newline."""
    with open(path, "w", encoding="utf-8") as f:
        for note in notes:
            f.write(note + "\n")


def load_notes(path):
    """Return the notes as a list of strings. Blank lines are skipped, a missing file gives []."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [line for line in lines if line.strip()]''',
        'load_notes on a missing file raises FileNotFoundError instead of returning [].'),
    'load_keeps_newlines': (r'''def save_notes(path, notes):
    """Write one note per line, replacing the file. Every line ends with a newline."""
    with open(path, "w", encoding="utf-8") as f:
        for note in notes:
            f.write(note + "\n")


def load_notes(path):
    """Return the notes as a list of strings. Blank lines are skipped, a missing file gives []."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []
    return [line for line in lines if line.strip()]''',
        'load_notes returns notes that still end with a newline character.'),
    'load_keeps_blank_lines': (r'''def save_notes(path, notes):
    """Write one note per line, replacing the file. Every line ends with a newline."""
    with open(path, "w", encoding="utf-8") as f:
        for note in notes:
            f.write(note + "\n")


def load_notes(path):
    """Return the notes as a list of strings. Blank lines are skipped, a missing file gives []."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return []
    return lines''',
        'blank lines come back as empty notes.'),
    'save_drops_last_note': (r'''def save_notes(path, notes):
    """Write one note per line, replacing the file. Every line ends with a newline."""
    with open(path, "w", encoding="utf-8") as f:
        for note in notes[:-1]:
            f.write(note + "\n")


def load_notes(path):
    """Return the notes as a list of strings. Blank lines are skipped, a missing file gives []."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return []
    return [line for line in lines if line.strip()]''',
        'the last note is not written.'),
    'load_strips_inner_spaces': (r'''def save_notes(path, notes):
    """Write one note per line, replacing the file. Every line ends with a newline."""
    with open(path, "w", encoding="utf-8") as f:
        for note in notes:
            f.write(note + "\n")


def load_notes(path):
    """Return the notes as a list of strings. Blank lines are skipped, a missing file gives []."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return []
    return [line.strip() for line in lines if line.strip()]''',
        "load_notes strips spaces around notes (the leading spaces of '  indented' are lost)."),
}

MIN_TESTS = 5


def test_tests_pass_on_the_correct_code():
    code, out, _ = run_suite(CORRECT)
    assert code != 5, ("No tests were collected. Write functions whose names start with test_ "
                       "in solution.py.")
    assert code == 0, ("Your tests must PASS on the correct code, but they failed or crashed. "
                       "A wrong expected value in your test is the usual cause. pytest said:\n"
                       + out[-1800:])


def test_you_wrote_enough_tests():
    names = [n.name for n in TESTS]
    assert len(names) >= MIN_TESTS, (
        f"Write at least {MIN_TESTS} test functions (names starting with test_); you have {len(names)}.")
    assert len(names) == len(set(names)), (
        "Two test functions share a name. The second silently replaces the first, so only one runs.")


def caught(name):
    source, why = MUTANTS[name]
    code, out, _ = run_suite(source)
    assert code == 1, (
        f"Your tests did NOT catch this bug: {why} "
        "Add a test whose expected value differs between the correct code and the buggy one."
        + ("" if code == 0 else f" (pytest exit code {code}; output: {out[-300:]})"))

def test_the_tests_really_use_tmp_path():
    users = [n for n in TESTS if "tmp_path" in arg_names(n)]
    assert len(users) >= 4, (
        "Write the files into pytest's tmp_path folder, never into a real folder: take tmp_path as a parameter in at least four tests. Found " + str(len(users)) + " test(s) taking tmp_path as a parameter.")


def test_catches_save_appends():
    caught('save_appends')


def test_catches_no_trailing_newline():
    caught('no_trailing_newline')


def test_catches_load_missing_raises():
    caught('load_missing_raises')


def test_catches_load_keeps_newlines():
    caught('load_keeps_newlines')


def test_catches_load_keeps_blank_lines():
    caught('load_keeps_blank_lines')


def test_catches_save_drops_last_note():
    caught('save_drops_last_note')


def test_catches_load_strips_inner_spaces():
    caught('load_strips_inner_spaces')
