from pathlib import Path

# The fixed bank package: audit.py imports balance lazily, inside report().

FILES = {
    "bank/__init__.py": '''from .accounts import balance, deposit, open_account, transfer
from .audit import history, report

__all__ = ["open_account", "deposit", "transfer", "balance", "history", "report"]
''',
    "bank/accounts.py": '''from .audit import log

_balances = {}


def open_account(name, amount=0):
    if name in _balances:
        raise ValueError(f"account {name} exists")
    _balances[name] = amount
    log(f"open {name} {amount}")


def deposit(name, amount):
    _balances[name] += amount
    log(f"deposit {name} {amount}")


def balance(name):
    return _balances[name]


def transfer(src, dst, amount):
    if _balances[src] < amount:
        raise ValueError("not enough money")
    _balances[src] -= amount
    _balances[dst] += amount
    log(f"transfer {src} {dst} {amount}")
''',
    "bank/audit.py": '''_entries = []


def log(event):
    _entries.append(event)


def history():
    return list(_entries)


def report(name):
    from .accounts import balance  # lazy: runs only when report() is called

    count = sum(1 for e in _entries if name in e.split()[1:3])
    return f"{name}: balance {balance(name)}, {count} events"
''',
}


def write_package(root):
    """Write every file in FILES under root. Return the sorted relative paths."""
    root = Path(root)
    for rel, text in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return sorted(FILES)
