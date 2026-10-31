import importlib
import subprocess
import sys

import pytest

from solution import split_script

PKG = "textkit"
SAMPLE = "The cat and the dog. A cat, a DOG, a cat!\n"
LAYOUT = ["textkit/__init__.py", "textkit/__main__.py", "textkit/clean.py", "textkit/reporting.py", "textkit/stats.py"]


def drop_pkg():
    for name in list(sys.modules):
        if name == PKG or name.startswith(PKG + "."):
            del sys.modules[name]


@pytest.fixture
def root(tmp_path, monkeypatch):
    drop_pkg()
    written = split_script(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    yield tmp_path, written
    drop_pkg()


def source(root_dir, name):
    return (root_dir / "textkit" / name).read_text(encoding="utf-8")


def run_module(root_dir, args, text):
    return subprocess.run([sys.executable, "-m", "textkit", *args], cwd=root_dir, input=text,
                          capture_output=True, text=True, timeout=20)


def test_layout(root):
    root_dir, written = root
    assert written == LAYOUT, "split_script returns the sorted relative paths. The package needs exactly these five files."
    for rel in LAYOUT:
        assert (root_dir / rel).is_file(), f"{rel} was not written."


def test_import_is_silent(root, capsys):
    import textkit  # noqa: F401
    import textkit.clean, textkit.stats, textkit.reporting  # noqa: E401,F401
    assert capsys.readouterr().out == "", "Importing the package must print nothing. The print(report(...)) line belongs in __main__.py only."


def test_functions_live_in_one_place(root):
    import textkit.clean as clean
    import textkit.reporting as reporting
    import textkit.stats as stats
    assert clean.words.__module__ == "textkit.clean" and clean.normalise.__module__ == "textkit.clean", "words and normalise are defined in clean.py."
    assert clean.STOP_WORDS == {"the", "a", "an", "and", "of", "to", "is"}, "STOP_WORDS lives in clean.py, unchanged."
    assert stats.count_words.__module__ == "textkit.stats" and stats.top_words.__module__ == "textkit.stats", "count_words and top_words are defined in stats.py."
    assert reporting.report.__module__ == "textkit.reporting", "report is defined in reporting.py."


def test_no_copied_definitions(root):
    root_dir, _ = root
    for name, banned in [("stats.py", ["def words", "def normalise", "def report", "STOP_WORDS ="]),
                         ("reporting.py", ["def words", "def normalise", "def count_words", "def top_words", "STOP_WORDS ="]),
                         ("__init__.py", ["def "]),
                         ("__main__.py", ["def report", "def words", "def top_words"])]:
        text = source(root_dir, name)
        for b in banned:
            assert b not in text, f"{name} contains {b!r}. Import it from the module that owns it instead of copying it."


def test_relative_imports(root):
    root_dir, _ = root
    for name in ["stats.py", "reporting.py", "__init__.py"]:
        assert "from ." in source(root_dir, name), f"{name} must import from its own package with a relative import (from .clean import words)."


def test_public_api(root):
    import textkit
    assert sorted(textkit.__all__) == ["count_words", "report", "top_words"], "__all__ lists exactly report, count_words and top_words."
    assert textkit.__version__ == "0.1.0", "Set __version__ = '0.1.0' in __init__.py."
    namespace = {}
    exec("from textkit import *", namespace)
    assert {"report", "count_words", "top_words"} <= set(namespace), "Star-import must give the three public names."
    assert "words" not in namespace and "normalise" not in namespace, "Star-import must not leak helpers. Check __all__."


def test_behaviour_unchanged(root):
    import textkit
    assert textkit.report(SAMPLE) == "words: 5\ncat: 3\ndog: 2", "report must give the same text as the old script."
    assert textkit.report(SAMPLE, 1) == "words: 5\ncat: 3", "n limits the number of top words."
    assert textkit.top_words("b a b c b c", 2) == [("b", 3), ("c", 2)], "top_words keeps most_common order and removes stop words."
    assert textkit.count_words("Is it? IT is.")["it"] == 2, "count_words lowercases and drops punctuation and stop words."
    assert textkit.report("") == "words: 0", "Empty text: only the 'words: 0' line."


def test_submodules_import_alone_in_fresh_python(root):
    root_dir, _ = root
    for mod in ["textkit.clean", "textkit.stats", "textkit.reporting", "textkit"]:
        proc = subprocess.run([sys.executable, "-c", f"import {mod}"], cwd=root_dir, input="",
                              capture_output=True, text=True, timeout=20)
        assert proc.returncode == 0, f"'import {mod}' fails in a fresh Python:\n{proc.stderr[-400:]}"
        assert proc.stdout == "", f"'import {mod}' printed something. Imports must be silent."


def test_python_dash_m(root):
    root_dir, _ = root
    proc = run_module(root_dir, [], SAMPLE)
    assert proc.returncode == 0, f"python -m textkit failed. Does textkit/__main__.py exist and use relative imports?\n{proc.stderr[-400:]}"
    assert proc.stdout == "words: 5\ncat: 3\ndog: 2\n", "python -m textkit reads stdin and prints the report."


def test_python_dash_m_with_n(root):
    root_dir, _ = root
    proc = run_module(root_dir, ["1"], SAMPLE)
    assert proc.stdout == "words: 5\ncat: 3\n", "The first command-line argument is N, the number of top words."
