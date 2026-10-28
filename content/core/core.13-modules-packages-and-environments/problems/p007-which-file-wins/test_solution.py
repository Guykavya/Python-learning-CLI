from importlib.machinery import PathFinder
from pathlib import Path

import pytest

from solution import find_module_file


@pytest.fixture
def tree(tmp_path):
    project = tmp_path / "project"
    lib = tmp_path / "lib"
    (project / "shop").mkdir(parents=True)
    (project / "shop" / "__init__.py").write_text("")
    (project / "random.py").write_text("")
    lib.mkdir()
    (lib / "random.py").write_text("")
    (lib / "shop.py").write_text("")
    (lib / "tools.py").write_text("")
    (project / "tools").mkdir()          # no __init__.py: does not count
    (project / "tools" / "helpers.py").write_text("")
    return project, lib


def same(got, expected):
    return got is not None and Path(got) == expected


def test_first_folder_wins(tree):
    project, lib = tree
    got = find_module_file("random", [project, lib])
    assert same(got, project / "random.py"), "Search the folders in the given order and stop at the first match."


def test_order_reversed(tree):
    project, lib = tree
    got = find_module_file("random", [str(lib), str(project)])
    assert same(got, lib / "random.py"), "With lib first, lib/random.py wins. Folders may also be strings."


def test_package_before_module_in_same_folder(tmp_path):
    (tmp_path / "shop").mkdir()
    (tmp_path / "shop" / "__init__.py").write_text("")
    (tmp_path / "shop.py").write_text("")
    got = find_module_file("shop", [tmp_path])
    assert same(got, tmp_path / "shop" / "__init__.py"), "Inside one folder, a package (shop/__init__.py) is found before shop.py."
    real = PathFinder.find_spec("shop", [str(tmp_path)])
    assert Path(real.origin) == tmp_path / "shop" / "__init__.py", "Real Python agrees: the package wins."


def test_folder_order_beats_kind(tree):
    project, lib = tree
    got = find_module_file("shop", [lib, project])
    assert same(got, lib / "shop.py"), "lib comes first, so lib/shop.py wins even though project has a package."


def test_folder_without_init_is_skipped(tree):
    project, lib = tree
    got = find_module_file("tools", [project, lib])
    assert same(got, lib / "tools.py"), "project/tools has no __init__.py, so it is not a match here. Keep searching."
    real = PathFinder.find_spec("tools", [str(project), str(lib)])
    assert Path(real.origin) == lib / "tools.py", "Real Python agrees: a regular module beats a namespace folder."


def test_not_found(tree):
    project, lib = tree
    assert find_module_file("nothing", [project, lib]) is None, "Return None when no folder has a match."


def test_missing_folder_is_skipped(tree, tmp_path):
    project, lib = tree
    got = find_module_file("shop", [tmp_path / "does_not_exist", lib])
    assert same(got, lib / "shop.py"), "Skip folders that do not exist instead of crashing."


def test_empty_list():
    assert find_module_file("random", []) is None, "No folders means nothing can be found: return None."
