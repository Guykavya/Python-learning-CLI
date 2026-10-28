import ast
import importlib
import subprocess
import sys

import pytest

from solution import write_package

PKG = "bank"


def drop_pkg():
    for name in list(sys.modules):
        if name == PKG or name.startswith(PKG + "."):
            del sys.modules[name]


@pytest.fixture
def root(tmp_path, monkeypatch):
    drop_pkg()
    write_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    yield tmp_path
    drop_pkg()


def fresh(root, code):
    return subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True, timeout=20)


def top_level_imports(path):
    """Names of the package modules imported at the top level of a file (not inside functions)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module:
                found.add(node.module.split(".")[-1])
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            found.update(alias.name.split(".")[-1] for alias in node.names)
    return found


@pytest.mark.parametrize("code", [
    "import bank",
    "import bank.audit",
    "import bank.accounts",
    "from bank.audit import report",
    "from bank import report, transfer",
])
def test_imports_work_in_fresh_python(root, code):
    proc = fresh(root, code)
    assert proc.returncode == 0, f"'{code}' still fails in a fresh Python. Is there still a cycle of top-level imports?\n{proc.stderr[-500:]}"


def test_cycle_is_broken_at_top_level(root):
    accounts = top_level_imports(root / "bank" / "accounts.py")
    audit = top_level_imports(root / "bank" / "audit.py")
    both = "audit" in accounts and "accounts" in audit
    assert not both, "accounts.py and audit.py still import each other at the top of the file. Move one of these imports inside the function that needs it."


def test_modules_not_merged(root):
    import bank.accounts
    import bank.audit
    assert bank.accounts.balance.__module__ == "bank.accounts", "balance stays in accounts.py."
    assert bank.audit.report.__module__ == "bank.audit", "report stays in audit.py."
    assert bank.audit.log.__module__ == "bank.audit", "log stays in audit.py."


def test_public_api(root):
    import bank
    assert sorted(bank.__all__) == sorted(["open_account", "deposit", "transfer", "balance", "history", "report"]), "Keep __all__ as it was."
    for name in bank.__all__:
        assert callable(getattr(bank, name, None)), f"bank.{name} must still be importable from the package."


def test_behaviour(root):
    import bank
    bank.open_account("asha", 100)
    bank.open_account("ravi")
    bank.transfer("asha", "ravi", 30)
    bank.deposit("ravi", 5)
    assert bank.balance("ravi") == 35, "Balances must work as before."
    assert bank.history() == ["open asha 100", "open ravi 0", "transfer asha ravi 30", "deposit ravi 5"], "Every action is logged in audit."
    assert bank.report("asha") == "asha: balance 70, 2 events", "report uses the real balance from accounts and counts the events of that person."
    assert bank.report("ravi") == "ravi: balance 35, 3 events", "The lazy import must reach the SAME accounts module (same _balances), not a new copy."


def test_errors_unchanged(root):
    import bank
    bank.open_account("x", 10)
    with pytest.raises(ValueError):
        bank.open_account("x")
    with pytest.raises(ValueError):
        bank.transfer("x", "x", 11)


def test_report_many_calls(root):
    import bank
    bank.open_account("a", 1)
    results = {bank.report("a") for _ in range(1000)}
    assert results == {"a: balance 1, 1 events"}, "A lazy import inside a function is cheap after the first call: the module comes from sys.modules."


def test_history_is_a_copy(root):
    import bank
    bank.open_account("a", 1)
    bank.history().append("fake")
    assert bank.history() == ["open a 1"], "history() still returns a copy of the list."
