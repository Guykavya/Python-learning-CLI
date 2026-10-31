import importlib
import json
import os
import sys

import pytest

from solution import dispatch, resolve

PKG = "toolbox"


def drop_pkg():
    for name in list(sys.modules):
        if name == PKG or name.startswith(PKG + "."):
            del sys.modules[name]


@pytest.fixture(autouse=True)
def toolbox(tmp_path, monkeypatch):
    files = {
        "toolbox/__init__.py": "from . import text\nVERSION = '1.0'\n",
        "toolbox/text.py": "def shout(args):\n    return ' '.join(args).upper() + '!'\n",
        "toolbox/sub/__init__.py": "",
        "toolbox/sub/maths.py": "def total(args):\n    return sum(int(a) for a in args)\n\nLIMIT = 10\n",
        "toolbox/needs_missing.py": "import package_that_does_not_exist_xyz\n\ndef f(args):\n    return 1\n",
    }
    for rel, code in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code, encoding="utf-8")
    drop_pkg()
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    yield
    drop_pkg()


def test_stdlib_targets():
    assert resolve("os.path:join") is os.path.join, "Import the part before ':' (os.path), then getattr the part after it (join)."
    assert resolve("json:dumps") is json.dumps, "'json:dumps' is json.dumps."


def test_returns_the_object_not_a_call():
    assert resolve("toolbox.sub.maths:LIMIT") == 10, "resolve returns the object it finds. It must not call it."


def test_submodule_target():
    f = resolve("toolbox.sub.maths:total")
    assert f(["2", "3"]) == 5, "Import the full dotted module 'toolbox.sub.maths' with importlib.import_module."


def test_dotted_attribute_path():
    f = resolve("toolbox:text.shout")
    assert f(["hi"]) == "HI!", "After the colon, follow every dotted name with getattr: toolbox -> .text -> .shout."
    assert resolve("toolbox:VERSION.upper")() == "1.0", "Attribute paths can go through any object, also a str."


@pytest.mark.parametrize("bad", ["json", "json:dumps:x", ":dumps", "json:", "a..b:f", "json:dumps.", "json:.dumps", ".json:dumps", ""])
def test_malformed_targets(bad):
    with pytest.raises(ValueError):
        resolve(bad)


def test_malformed_checked_before_import():
    with pytest.raises(ValueError):
        resolve("module_that_does_not_exist_xyz")
    assert "module_that_does_not_exist_xyz" not in sys.modules, "A target without ':' is malformed. Raise ValueError before you try any import."


def test_missing_module_error_goes_up():
    with pytest.raises(ModuleNotFoundError):
        resolve("toolbox.nothere:f")


def test_error_inside_module_is_not_hidden():
    with pytest.raises(ModuleNotFoundError) as info:
        resolve("toolbox.needs_missing:f")
    assert "package_that_does_not_exist_xyz" in str(info.value), "An import error inside the target module must reach the user unchanged. Do not catch it and raise something vaguer."


def test_missing_attribute_names_the_target():
    with pytest.raises(AttributeError) as info:
        resolve("toolbox.text:whisper")
    assert "toolbox.text:whisper" in str(info.value), "The AttributeError message must contain the whole target, so the user can find the wrong config line."
    with pytest.raises(AttributeError) as info:
        resolve("toolbox:text.nope")
    assert "toolbox:text.nope" in str(info.value), "Same for a missing name deeper in the attribute path."


def test_dispatch_calls_with_args():
    table = {"shout": "toolbox.text:shout", "total": "toolbox.sub.maths:total"}
    assert dispatch(table, "shout", ["good", "morning"]) == "GOOD MORNING!", "dispatch resolves the target and calls it with the args list."
    assert dispatch(table, "total", ["1", "2", "3"]) == 6, "Return what the function returns."


def test_dispatch_unknown_command():
    with pytest.raises(KeyError):
        dispatch({"a": "json:dumps"}, "b", [])


def test_dispatch_not_callable():
    with pytest.raises(TypeError):
        dispatch({"limit": "toolbox.sub.maths:LIMIT"}, "limit", [])


def test_dispatch_imports_lazily():
    table = {"shout": "toolbox.text:shout", "broken": "toolbox.needs_missing:f"}
    assert dispatch(table, "shout", ["x"]) == "X!", "Only resolve the command that is asked for. A broken target for another command must not matter."
