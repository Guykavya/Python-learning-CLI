import importlib
import shutil
import sys

import pytest

from solution import write_unitkit

PUBLIC = ["to_miles", "to_km", "to_fahrenheit", "to_celsius"]


def drop():
    for n in list(sys.modules):
        if n == "unitkit" or n.startswith("unitkit.") or n.startswith("c13p11_") or n in ("_rounding", "length", "temperature"):
            del sys.modules[n]


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    drop()
    yield
    drop()


@pytest.fixture
def unitkit(tmp_path, monkeypatch):
    write_unitkit(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    return importlib.import_module("unitkit")


def test_files_exist(tmp_path):
    write_unitkit(str(tmp_path))
    for name in ("__init__.py", "_rounding.py", "length.py", "temperature.py"):
        assert (tmp_path / "unitkit" / name).is_file(), f"Write unitkit/{name} inside root."


def test_import_prints_nothing(tmp_path, monkeypatch, capsys):
    write_unitkit(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    importlib.import_module("unitkit")
    assert capsys.readouterr().out == "", "Importing a package must not print. Remove test prints from the files."


def test_length(unitkit):
    assert unitkit.to_miles(10) == 6.21, "to_miles(10) is r2(10 * 0.621371) = 6.21."
    assert unitkit.to_km(10) == 16.09, "to_km(10) is r2(10 * 1.609344) = 16.09."


def test_temperature(unitkit):
    assert unitkit.to_fahrenheit(37) == 98.6, "to_fahrenheit(37) is r2(37 * 9 / 5 + 32) = 98.6."
    assert unitkit.to_celsius(212) == 100.0, "to_celsius(212) is r2((212 - 32) * 5 / 9) = 100.0."
    assert unitkit.to_celsius(100) == 37.78, "Round to 2 places with r2: 37.777... becomes 37.78."


def test_submodules_reachable(unitkit):
    assert unitkit.length.to_km(1) == 1.61, "unitkit.length is the submodule; its functions work there too."
    assert unitkit.temperature.to_fahrenheit(0) == 32.0, "unitkit.temperature.to_fahrenheit(0) is 32.0."


def test_reexported_not_copied(unitkit):
    assert unitkit.to_miles.__module__ == "unitkit.length", (
        "to_miles must be defined in length.py and imported into __init__.py, not written again in __init__.py."
    )
    assert unitkit.to_celsius.__module__ == "unitkit.temperature", "to_celsius must be defined in temperature.py and re-exported."


def test_shared_private_helper(unitkit):
    rounding = sys.modules.get("unitkit._rounding")
    assert rounding is not None, "length.py and temperature.py should import r2 from the private module unitkit/_rounding.py."
    assert unitkit.length.r2 is rounding.r2 and unitkit.temperature.r2 is rounding.r2, (
        "Both modules must use the one r2 from _rounding.py (from ._rounding import r2), not their own copies."
    )


def test_version(unitkit):
    assert unitkit.__version__ == "1.0.0", "Set __version__ = '1.0.0' in __init__.py."


def test_all_and_star(unitkit):
    assert list(unitkit.__all__) == PUBLIC, f"__all__ must be exactly {PUBLIC}."
    ns = {}
    exec("from unitkit import *", ns)
    got = sorted(k for k in ns if k != "__builtins__")
    assert got == sorted(PUBLIC), "from unitkit import * must bring in exactly the four public functions."


def test_helper_not_public(unitkit):
    assert not hasattr(unitkit, "r2"), "r2 is a private helper. Do not import it in __init__.py."


def test_relative_imports_survive_rename(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    write_unitkit(src)
    other = tmp_path / "other"
    other.mkdir()
    shutil.copytree(src / "unitkit", other / "c13p11_renamed")
    monkeypatch.syspath_prepend(str(other))   # only the renamed copy is on sys.path
    importlib.invalidate_caches()
    try:
        mod = importlib.import_module("c13p11_renamed")
    except ModuleNotFoundError as e:
        pytest.fail(
            f"The renamed package failed to import ({e}). Use relative imports like `from ._rounding import r2` "
            "instead of `from unitkit._rounding import ...` or `from _rounding import ...`."
        )
    assert mod.to_miles(10) == 6.21, "The renamed package should still work."
