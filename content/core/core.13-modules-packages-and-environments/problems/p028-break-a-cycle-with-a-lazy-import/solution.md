## Approach

Why it fails: `import bank` runs `bank/__init__.py`, which starts `bank.accounts`. Line 1 of
`accounts.py` starts `bank.audit`. Line 1 of `audit.py` runs `from .accounts import balance`.
`bank.accounts` is in `sys.modules` already, but it is still on its first line, so it has no
`balance` yet: `ImportError ... partially initialized module`.

The cure is to make one side stop needing the other **at load time**. `audit` only needs `balance`
inside `report`, so its import moves there. When `report` is called, `accounts` has long finished
loading, and the import just takes it from `sys.modules`. The modules stay separate and the public API
does not change.

## Code

The only change is in `bank/audit.py`:

```python
_entries = []


def log(event):
    _entries.append(event)


def history():
    return list(_entries)


def report(name):
    from .accounts import balance  # lazy: runs only when report() is called

    count = sum(1 for e in _entries if name in e.split()[1:3])
    return f"{name}: balance {balance(name)}, {count} events"
```

## Complexity

The first call of `report` finishes the import (a dictionary lookup in `sys.modules`, since `accounts`
is loaded already); later calls are the same cheap lookup. The rest is O(E) for E log entries.

## Another way

1. **Import the module, not the name**: `from . import accounts` at the top of `audit.py`, and
   `accounts.balance(name)` inside `report`. Since Python 3.7 this works with a half-built module, because
   the name is looked up only when `report` runs. The cycle is still there, though, and fragile.
2. **Remove the cycle by design** (the best long-term fix): move `log` and `_entries` into a new module
   `bank/events.py` that imports nothing from the package. `accounts` and `audit` both import from
   `events`, and `audit` may then import `accounts` at the top. The arrows point one way again
   (see p025).
