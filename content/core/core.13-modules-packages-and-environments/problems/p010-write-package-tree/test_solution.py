import importlib
import sys

import pytest

from solution import write_package


@pytest.fixture(autouse=True)
def clean(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(tmp_path))
    drop = lambda: [sys.modules.pop(n) for n in list(sys.modules) if n.startswith("c13p10_")]
    drop()
    yield
    drop()


FILES = {
    "c13p10_kit/__init__.py": "from .basic import add\n",
    "c13p10_kit/basic.py": "def add(a, b):\n    return a + b\n",
    "c13p10_kit/stats/mean.py": "def mean(xs):\n    return sum(xs) / len(xs)\n",
    "main.py": "import c13p10_kit\n",
}


def test_return_value(tmp_path):
    got = write_package(tmp_path, FILES)
    assert got == [
        "c13p10_kit/__init__.py",
        "c13p10_kit/basic.py",
        "c13p10_kit/stats/__init__.py",
        "c13p10_kit/stats/mean.py",
        "main.py",
    ], "Return all written paths, sorted, with '/' separators, including the __init__.py you added."


def test_files_written(tmp_path):
    write_package(str(tmp_path), FILES)
    assert (tmp_path / "c13p10_kit" / "stats" / "mean.py").read_text(encoding="utf-8") == FILES["c13p10_kit/stats/mean.py"], (
        "Write each file's text under root. Create missing folders with mkdir(parents=True, exist_ok=True)."
    )
    assert (tmp_path / "main.py").exists(), "Files directly in root are written too."


def test_missing_init_added_empty(tmp_path):
    write_package(tmp_path, FILES)
    init = tmp_path / "c13p10_kit" / "stats" / "__init__.py"
    assert init.exists(), "The subpackage folder stats/ needs its own __init__.py."
    assert init.read_text() == "", "An added __init__.py is empty."


def test_given_init_kept(tmp_path):
    write_package(tmp_path, FILES)
    text = (tmp_path / "c13p10_kit" / "__init__.py").read_text(encoding="utf-8")
    assert text == "from .basic import add\n", "Do not overwrite an __init__.py that the dict gives you."


def test_no_init_in_root(tmp_path):
    write_package(tmp_path, FILES)
    assert not (tmp_path / "__init__.py").exists(), "root itself is not a package: do not add root/__init__.py."


def test_deep_folders_all_get_init(tmp_path):
    got = write_package(tmp_path, {"c13p10_a/b/c/leaf.py": "X = 1\n"})
    assert got == [
        "c13p10_a/__init__.py",
        "c13p10_a/b/__init__.py",
        "c13p10_a/b/c/__init__.py",
        "c13p10_a/b/c/leaf.py",
    ], "Every folder between root and the file needs __init__.py, not only the last one."


def test_package_imports(tmp_path):
    write_package(tmp_path, FILES)
    importlib.invalidate_caches()
    kit = importlib.import_module("c13p10_kit")
    assert kit.add(2, 3) == 5, "The package __init__ re-exports add from basic."
    mean_mod = importlib.import_module("c13p10_kit.stats.mean")
    assert mean_mod.mean([1, 2, 3]) == 2, "The subpackage module should import and work."
    stats = importlib.import_module("c13p10_kit.stats")
    assert stats.__file__ is not None, (
        "stats has no __init__.py, so Python made it a namespace package (__file__ is None). Add the empty __init__.py."
    )


def test_input_dict_not_changed(tmp_path):
    files = {"c13p10_x/m.py": "Y = 2\n"}
    write_package(tmp_path, files)
    assert files == {"c13p10_x/m.py": "Y = 2\n"}, "Do not add the __init__ entries to the caller's dict. Work on a copy."
