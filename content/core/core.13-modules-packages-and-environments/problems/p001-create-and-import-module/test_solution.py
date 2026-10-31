import sys

import pytest

from solution import create_module

NAMES = ("c13p1_greet", "c13p1_maths", "c13p1_other")


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    for n in NAMES:
        sys.modules.pop(n, None)
    yield
    for n in NAMES:
        sys.modules.pop(n, None)


GREET = 'def hello(name):\n    return f"Hello, {name}!"\n'


def test_returns_module_object(tmp_path):
    mod = create_module(tmp_path, "c13p1_greet", GREET)
    assert mod is not None, "Return the module object that the import gives you, not None."
    assert mod.__name__ == "c13p1_greet", "The module's __name__ is the file name without .py."
    assert mod.hello("Kavya") == "Hello, Kavya!", "The returned module should run the source you wrote."


def test_file_is_written(tmp_path):
    create_module(str(tmp_path), "c13p1_greet", GREET)
    f = tmp_path / "c13p1_greet.py"
    assert f.exists(), "Write the source into <folder>/<name>.py. Did you forget the .py suffix?"
    assert f.read_text(encoding="utf-8") == GREET, "Write the source exactly as given."


def test_folder_at_front_once(tmp_path):
    create_module(tmp_path, "c13p1_greet", GREET)
    create_module(tmp_path, "c13p1_maths", "def double(x):\n    return 2 * x\n")
    assert sys.path[0] == str(tmp_path), "Insert str(folder) at the front of sys.path (index 0), not at the end."
    assert sys.path.count(str(tmp_path)) == 1, "Add the folder only once. Check `in sys.path` before inserting."


def test_two_modules_same_folder(tmp_path):
    a = create_module(tmp_path, "c13p1_greet", GREET)
    b = create_module(tmp_path, "c13p1_maths", "def double(x):\n    return 2 * x\n")
    assert b.double(21) == 42, "The second module was not found. Call importlib.invalidate_caches() after writing."
    assert a.hello("A") == "Hello, A!", "The first module should still work."


def test_module_is_cached(tmp_path):
    mod = create_module(tmp_path, "c13p1_greet", GREET)
    assert sys.modules.get("c13p1_greet") is mod, "A real import stores the module in sys.modules. Use importlib.import_module."


def test_new_source_replaces_cached_module(tmp_path):
    create_module(tmp_path, "c13p1_greet", GREET)
    mod = create_module(tmp_path, "c13p1_greet", 'def hello(name):\n    return "Hi " + name + ", welcome back"\n')
    assert mod.hello("Kavya") == "Hi Kavya, welcome back", (
        "The old code is cached in sys.modules, so a plain import returns it again. Use importlib.reload."
    )
