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
def run_suite(target_source, extra=(), poison=False):
    with tempfile.TemporaryDirectory(prefix="learn-mut-") as tmp:
        tmp = Path(tmp)
        (tmp / "target.py").write_text(target_source)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1")
        # The real environment must not matter: always run with APP_* set to junk, so tests that
        # forget monkeypatch.delenv fail here.
        env["APP_MODE"] = "from-the-real-environment"
        env["APP_PORT"] = "1234"
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

CORRECT = r'''import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    path = Path("config.txt")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    if "APP_MODE" in os.environ:
        cfg["mode"] = os.environ["APP_MODE"]
    if "APP_PORT" in os.environ:
        cfg["port"] = os.environ["APP_PORT"]
    cfg["port"] = int(cfg["port"])
    return cfg'''

MUTANTS = {
    'env_mode_ignored': (r'''import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    path = Path("config.txt")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    if "APP_PORT" in os.environ:
        cfg["port"] = os.environ["APP_PORT"]
    cfg["port"] = int(cfg["port"])
    return cfg''',
        'the APP_MODE environment variable is ignored.'),
    'env_port_ignored': (r'''import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    path = Path("config.txt")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    if "APP_MODE" in os.environ:
        cfg["mode"] = os.environ["APP_MODE"]
    cfg["port"] = int(cfg["port"])
    return cfg''',
        'the APP_PORT environment variable is ignored.'),
    'port_stays_string': (r'''import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    path = Path("config.txt")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    if "APP_MODE" in os.environ:
        cfg["mode"] = os.environ["APP_MODE"]
    if "APP_PORT" in os.environ:
        cfg["port"] = os.environ["APP_PORT"]
    return cfg''',
        "the port is returned as a string ('9000') instead of an int."),
    'file_ignored': (r'''import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    path = Path("config.txt")
    if False:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    if "APP_MODE" in os.environ:
        cfg["mode"] = os.environ["APP_MODE"]
    if "APP_PORT" in os.environ:
        cfg["port"] = os.environ["APP_PORT"]
    cfg["port"] = int(cfg["port"])
    return cfg''',
        'config.txt in the current folder is never read.'),
    'file_beats_env': (r'''import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    if "APP_MODE" in os.environ:
        cfg["mode"] = os.environ["APP_MODE"]
    if "APP_PORT" in os.environ:
        cfg["port"] = os.environ["APP_PORT"]
    path = Path("config.txt")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    cfg["port"] = int(cfg["port"])
    return cfg''',
        'environment variables must win over the file.'),
    'comments_kept': (r'''import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    path = Path("config.txt")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    if "APP_MODE" in os.environ:
        cfg["mode"] = os.environ["APP_MODE"]
    if "APP_PORT" in os.environ:
        cfg["port"] = os.environ["APP_PORT"]
    cfg["port"] = int(cfg["port"])
    return cfg''',
        'comment lines are parsed as settings and pollute the dict.'),
    'values_not_stripped': (r'''import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    path = Path("config.txt")
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value
    if "APP_MODE" in os.environ:
        cfg["mode"] = os.environ["APP_MODE"]
    if "APP_PORT" in os.environ:
        cfg["port"] = os.environ["APP_PORT"]
    cfg["port"] = int(cfg["port"])
    return cfg''',
        "spaces around the value are kept ('test ' instead of 'test')."),
    'missing_file_crashes': (r'''import os
from pathlib import Path


def load_config():
    """Defaults, then config.txt in the current folder, then the APP_MODE / APP_PORT variables."""
    cfg = {"mode": "dev", "port": 8000, "name": "app"}
    path = Path("config.txt")
    if True:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    if "APP_MODE" in os.environ:
        cfg["mode"] = os.environ["APP_MODE"]
    if "APP_PORT" in os.environ:
        cfg["port"] = os.environ["APP_PORT"]
    cfg["port"] = int(cfg["port"])
    return cfg''',
        'a missing config.txt makes load_config crash instead of using the defaults.'),
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

def test_you_isolate_the_environment_and_the_folder():
    src = LEARNER_SOURCE
    assert "monkeypatch.chdir" in src, (
        "Run each test inside tmp_path with monkeypatch.chdir(tmp_path); otherwise load_config "
        "reads a config.txt from whatever folder pytest was started in.")
    assert "monkeypatch.setenv" in src and "monkeypatch.delenv" in src, (
        "Use monkeypatch.setenv to set a variable and monkeypatch.delenv(name, raising=False) to make sure "
        "it is absent, so the real environment of your computer cannot change the result.")


def test_catches_env_mode_ignored():
    caught('env_mode_ignored')


def test_catches_env_port_ignored():
    caught('env_port_ignored')


def test_catches_port_stays_string():
    caught('port_stays_string')


def test_catches_file_ignored():
    caught('file_ignored')


def test_catches_file_beats_env():
    caught('file_beats_env')


def test_catches_comments_kept():
    caught('comments_kept')


def test_catches_values_not_stripped():
    caught('values_not_stripped')


def test_catches_missing_file_crashes():
    caught('missing_file_crashes')
