# Break a circular import with a lazy import

The `bank` package worked until someone added `report` to `audit.py`. Now even `import bank` fails:

```text
ImportError: cannot import name 'balance' from partially initialized module 'bank.accounts'
(most likely due to a circular import)
```

The three files are in the dict `FILES` in your `starter.py`. Here is the important part:

```python
# bank/__init__.py
from .accounts import balance, deposit, open_account, transfer
from .audit import history, report

# bank/accounts.py
from .audit import log            # accounts needs audit.log in every function
_balances = {}
...

# bank/audit.py
from .accounts import balance     # audit needs accounts.balance, but only in report()
_entries = []

def log(event): ...
def history(): ...
def report(name):
    count = sum(1 for e in _entries if name in e.split()[1:3])
    return f"{name}: balance {balance(name)}, {count} events"
```

Your tasks:

1. Explain to yourself, line by line, why the import fails: which module starts first, where it stops,
   and which name is missing at that moment.
2. Fix the package by editing the texts in `FILES`. Break the cycle with a **lazy import**: move the
   import into the one function that needs it, so it runs when the function is **called**, not when
   the module is loaded. After the fix, at least one of `accounts.py` and `audit.py` must no longer
   import the other at the top of the file.
3. Do not merge the two modules, and do not change the public API or the behaviour.

`write_package(root)` (already written) puts the files under `root`. The tests import the package
from there, in this process and in fresh Python processes.

## Example

After the fix:

```python
>>> import bank
>>> bank.open_account("asha", 100)
>>> bank.open_account("ravi")
>>> bank.transfer("asha", "ravi", 30)
>>> bank.balance("ravi")
30
>>> bank.history()
['open asha 100', 'open ravi 0', 'transfer asha ravi 30']
>>> bank.report("asha")
'asha: balance 70, 2 events'
```

`report` counts the events where the name is the second or third word of the entry
(`e.split()[1:3]`), so the transfer counts for both people.
