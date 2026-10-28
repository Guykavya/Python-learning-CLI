import json
import os.path
import sys

import pytest

from solution import import_or_default

NAMES = ("c13p8_broken", "c13p8_angry", "c13p8_good", "c13p8_pkg", "c13p8_pkg.inner")


@pytest.fixture(autouse=True)
def clean(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(tmp_path))
    for n in NAMES:
        sys.modules.pop(n, None)
    yield
    for n in NAMES:
        sys.modules.pop(n, None)


def test_existing_stdlib_module():
    assert import_or_default("json") is json, "Return the module object itself; importing json twice gives the same object."


def test_dotted_name():
    assert import_or_default("os.path") is os.path, "import_module accepts dotted names like 'os.path'."


def test_missing_returns_default():
    assert import_or_default("c13p8_no_such_lib", "plain") == "plain", "A missing module gives the default."
    assert import_or_default("c13p8_no_such_lib") is None, "The default default is None."


def test_missing_parent_returns_default():
    assert import_or_default("c13p8_no_such_lib.sub", 0) == 0, (
        "For 'a.sub' the error names 'a', the parent. A missing parent also means the module does not exist."
    )


def test_missing_submodule_returns_default(tmp_path):
    (tmp_path / "c13p8_pkg").mkdir()
    (tmp_path / "c13p8_pkg" / "__init__.py").write_text("")
    assert import_or_default("c13p8_pkg.inner", "none") == "none", "The package exists but pkg.inner does not: return the default."


def test_local_module(tmp_path):
    (tmp_path / "c13p8_good.py").write_text("VALUE = 42\n")
    mod = import_or_default("c13p8_good")
    assert mod is not None and mod.VALUE == 42, "Modules on sys.path (not only stdlib) must import normally."


def test_broken_dependency_is_not_hidden(tmp_path):
    (tmp_path / "c13p8_broken.py").write_text("import c13p8_not_installed_dependency\n")
    with pytest.raises(ModuleNotFoundError) as info:
        import_or_default("c13p8_broken", "fallback")
    assert info.value.name == "c13p8_not_installed_dependency", (
        "c13p8_broken exists, but it imports a missing module. Re-raise that error; "
        "do not return the default for every ModuleNotFoundError."
    )


def test_other_errors_go_up(tmp_path):
    (tmp_path / "c13p8_angry.py").write_text("raise ValueError('bad config')\n")
    with pytest.raises(ValueError):
        import_or_default("c13p8_angry", "fallback")


def test_similar_prefix_is_not_a_parent(tmp_path):
    # the error names 'c13p8_bro', which is NOT a parent of 'c13p8_broken'
    (tmp_path / "c13p8_broken.py").write_text("import c13p8_bro\n")
    with pytest.raises(ModuleNotFoundError):
        import_or_default("c13p8_broken")
