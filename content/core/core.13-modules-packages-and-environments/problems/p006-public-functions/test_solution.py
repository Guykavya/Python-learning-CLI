import importlib
import sys

import pytest

from solution import public_functions

NAMES = ("c13p6_shapes", "c13p6_base", "c13p6_user", "c13p6_empty")


@pytest.fixture(autouse=True)
def clean(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(tmp_path))
    for n in NAMES:
        sys.modules.pop(n, None)
    yield
    for n in NAMES:
        sys.modules.pop(n, None)


def load(tmp_path, name, source):
    (tmp_path / f"{name}.py").write_text(source, encoding="utf-8")
    importlib.invalidate_caches()
    return importlib.import_module(name)


SHAPES = '''
from math import pi, sqrt
import json
from os.path import join as join_paths

RATE = 2
_cache = {}


def area(r):
    return pi * r * r


def _helper():
    return 1


def side_from_area(a):
    return sqrt(a)


double = lambda x: x * RATE
say = print
'''


def test_example(tmp_path):
    mod = load(tmp_path, "c13p6_shapes", SHAPES)
    assert public_functions(mod) == ["area", "double", "side_from_area"], (
        "Keep only public callables whose __module__ equals module.__name__. "
        "Imported functions like sqrt and join_paths, modules like json, and print must be left out."
    )


def test_no_private_names(tmp_path):
    mod = load(tmp_path, "c13p6_shapes", SHAPES)
    got = public_functions(mod)
    assert all(not n.startswith("_") for n in got), "Skip names that start with _ (private helpers and __dunder__ names)."


def test_returns_sorted_list(tmp_path):
    mod = load(tmp_path, "c13p6_shapes", "def zeta():\n    pass\n\n\ndef alpha():\n    pass\n\n\ndef mid():\n    pass\n")
    got = public_functions(mod)
    assert isinstance(got, list), "Return a list."
    assert got == ["alpha", "mid", "zeta"], "Return the names sorted alphabetically."


def test_function_imported_from_sibling(tmp_path):
    load(tmp_path, "c13p6_base", "def shared():\n    return 1\n\n\ndef own_base():\n    return 2\n")
    user = load(tmp_path, "c13p6_user", "from c13p6_base import shared\nimport c13p6_base\n\n\ndef own():\n    return shared()\n")
    assert public_functions(user) == ["own"], (
        "shared() was defined in c13p6_base, so its __module__ is 'c13p6_base'. Only list functions defined in this module."
    )


def test_empty_module(tmp_path):
    mod = load(tmp_path, "c13p6_empty", "X = 1\n")
    assert public_functions(mod) == [], "A module with no functions gives an empty list. Constants are not callable."
