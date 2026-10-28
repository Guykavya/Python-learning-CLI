import importlib
import subprocess
import sys

import pytest

from solution import write_app


def drop():
    for n in list(sys.modules):
        if n == "invoices" or n.startswith("invoices.") or n in ("money", "sample_data"):
            del sys.modules[n]


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    drop()
    yield
    drop()


def load(tmp_path, monkeypatch, name="invoices"):
    write_app(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as e:
        pytest.fail(
            f"import {name} failed: {e}. Inside a package, import a sibling module with a relative "
            "import: `from .money import ...`. A plain `from money import ...` looks for a top-level module."
        )
    except ImportError as e:
        pytest.fail(
            f"import {name} failed: {e}. 'partially initialized module' means a circular import: "
            "money imports totals while totals is still importing money. Make the imports go one way only."
        )


def test_package_imports(tmp_path, monkeypatch):
    invoices = load(tmp_path, monkeypatch)
    assert invoices.invoice_total([(100, 2), (50, 1)]) == "Rs 295.00", "250 plus 18% tax is 295.00."


def test_money_functions(tmp_path, monkeypatch):
    load(tmp_path, monkeypatch)
    money = importlib.import_module("invoices.money")
    assert money.fmt(295) == "Rs 295.00", "Keep fmt in invoices/money.py and its format 'Rs 295.00'."
    assert abs(money.with_tax(100) - 118.0) < 1e-9, "with_tax(100) adds 18%: 118.0. Keep the tax rate at 0.18."


def test_import_money_first(tmp_path, monkeypatch):
    money = load(tmp_path, monkeypatch, "invoices.money")
    assert money.fmt(1) == "Rs 1.00", "Importing invoices.money first must work too. Check for a remaining import cycle."


def test_invoice_total_empty_and_tax(tmp_path, monkeypatch):
    invoices = load(tmp_path, monkeypatch)
    assert invoices.invoice_total([]) == "Rs 0.00", "No items is a total of 0."
    assert invoices.invoice_total([(10, 3)]) == "Rs 35.40", "30 plus 18% tax is 35.40."


def test_no_file_shadows_the_standard_library(tmp_path):
    write_app(tmp_path)
    clashes = sorted(
        p.name for p in tmp_path.iterdir()
        if (p.suffix == ".py" and p.stem in sys.stdlib_module_names) or (p.is_dir() and p.name in sys.stdlib_module_names)
    )
    assert clashes == [], (
        f"{clashes} has the name of a standard library module. The script's folder is first in sys.path, "
        "so `import json` loads this file instead of the real json. Rename it."
    )


def test_report_runs(tmp_path):
    write_app(tmp_path)
    proc = subprocess.run(
        [sys.executable, "report.py"], cwd=tmp_path, capture_output=True, text=True, timeout=20,
    )
    assert proc.returncode == 0, "python report.py crashed:\n" + proc.stderr[-800:]
    assert proc.stdout.splitlines() == ["Rs 295.00", '{"lines": 2}'], (
        "report.py should print the total and then the JSON line. Got:\n" + proc.stdout
    )
