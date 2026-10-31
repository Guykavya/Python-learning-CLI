import importlib.util
from pathlib import Path

import pytest

import solution
from solution import relative_name, resolve_relative


def test_does_not_use_resolve_name():
    text = Path(solution.__file__).read_text(encoding="utf-8")
    assert "resolve_name" not in text, "Build the rule yourself: do not call importlib.util.resolve_name."


@pytest.mark.parametrize("name, module, is_pkg, expected", [
    (".utils", "shop.api.views", False, "shop.api.utils"),
    ("..core.db", "shop.api.views", False, "shop.core.db"),
    ("..", "shop.api.views", False, "shop"),
    (".", "shop.api.views", False, "shop.api"),
    (".views", "shop.api", True, "shop.api.views"),
    ("..core", "shop.api", True, "shop.core"),
    (".", "shop", True, "shop"),
    (".models", "shop.cart", False, "shop.models"),
    ("....d", "a.b.c.d.e", False, "a.d"),
])
def test_resolves(name, module, is_pkg, expected):
    got = resolve_relative(name, module, is_pkg)
    assert got == expected, f"resolve_relative({name!r}, {module!r}, {is_pkg}) should be {expected!r}, got {got!r}. One dot = the package itself; each extra dot goes one level up."
    package = module if is_pkg else module.rpartition(".")[0]
    assert importlib.util.resolve_name(name, package) == expected, "(check of the test data itself against Python's own rule)"


def test_package_init_is_its_own_package():
    assert resolve_relative(".x", "shop.api", is_package=True) == "shop.api.x", "In __init__.py the module name IS the package. Do not cut off the last part when is_package is True."
    assert resolve_relative(".x", "shop.api", is_package=False) == "shop.x", "For a normal module, the package is the name without its last part."


def test_absolute_name_unchanged():
    assert resolve_relative("json", "shop.api.views") == "json", "A name without a leading dot is absolute already."
    assert resolve_relative("os.path", "main") == "os.path", "Absolute names work even without a package."


def test_beyond_top_level():
    with pytest.raises(ImportError) as info:
        resolve_relative("...x", "shop.api.views")
    assert "beyond top-level package" in str(info.value), "shop.api has 2 parts; three dots go up 2 levels, above 'shop'. Raise ImportError('attempted relative import beyond top-level package')."
    with pytest.raises(ImportError):
        resolve_relative("..", "shop", is_package=True)


def test_no_parent_package():
    with pytest.raises(ImportError) as info:
        resolve_relative(".helpers", "main")
    assert "no known parent package" in str(info.value), "A top-level module has an empty package. This is the famous error you get from running a package file directly."
    with pytest.raises(ImportError):
        resolve_relative(".", "__main__")


@pytest.mark.parametrize("target, module, is_pkg, expected", [
    ("shop.api.utils", "shop.api.views", False, ".utils"),
    ("shop.core.db", "shop.api.views", False, "..core.db"),
    ("shop.api", "shop.api.views", False, "."),
    ("shop", "shop.api.views", False, ".."),
    ("shop.api.views", "shop.api", True, ".views"),
    ("shop.core", "shop.api", True, "..core"),
    ("shop.api.views", "shop.api.views", False, ".views"),
    ("a.x.y", "a.b.c.d.e", False, "....x.y"),
])
def test_relative_name(target, module, is_pkg, expected):
    got = relative_name(target, module, is_pkg)
    assert got == expected, f"relative_name({target!r}, {module!r}, {is_pkg}) should be {expected!r}, got {got!r}. Find how many leading parts target shares with the package, go up the rest."
    assert resolve_relative(got, module, is_pkg) == target, "Both functions must agree: resolving the relative name gives the target back."


def test_relative_name_shortest():
    assert relative_name("shop.api.utils", "shop.api.views") == ".utils", "Do not go up and back down ('..api.utils'). Use the longest common start."


def test_relative_name_partial_word_is_not_common():
    assert relative_name("shop.apiary", "shop.api.views") == "..apiary", "Compare whole parts, not characters: 'apiary' is not inside 'api'."


def test_relative_name_impossible():
    with pytest.raises(ValueError):
        relative_name("other.x", "shop.api.views")
    with pytest.raises(ValueError):
        relative_name("shop.x", "main")
