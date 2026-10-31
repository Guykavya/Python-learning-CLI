## Approach

Fix one error at a time, and read each traceback from the bottom.

**Bug 1: `ModuleNotFoundError: No module named 'money'`.** In `totals.py`, `from money import ...` is an
absolute import: Python looks for a **top-level** module `money` in the folders of `sys.path`. The folder
`root/` is on the path, but `root/invoices/` is not. A module in the same package is reached with a
relative import: `from .money import fmt, with_tax`. (It "worked" for Arjun only when he ran things from
inside `invoices/`.)

**Bug 2: `cannot import name 'TAX_RATE' from partially initialized module 'invoices.totals'`.** Follow
the imports: `__init__` → `totals`; the first line of `totals` → `money`; the first line of `money` →
`totals`. `totals` is already in `sys.modules`, but only its first line has run, so `TAX_RATE` does not
exist yet. That is a **circular import**. The cure is to make the arrows go one way. `TAX_RATE` is a
money detail, so it moves into `money.py`; now `totals` needs `money`, and `money` needs nothing.
(Another common cure: move shared values into a third module like `config.py` that imports nothing.)

**Bug 3: `AttributeError: module 'json' has no attribute 'dumps'`.** When you run `python report.py`,
the script's folder is `sys.path[0]`, so `import json` finds Arjun's `json.py` before the standard
library. Rename the helper (`sample_data.py`) and import it by its new name.

## Code

```python
from pathlib import Path

FILES = {
    "invoices/__init__.py": """from .totals import invoice_total
""",
    "invoices/money.py": """TAX_RATE = 0.18


def fmt(amount):
    return f"Rs {amount:.2f}"


def with_tax(amount):
    return amount * (1 + TAX_RATE)
""",
    "invoices/totals.py": """from .money import fmt, with_tax


def invoice_total(items):
    subtotal = sum(price * qty for price, qty in items)
    return fmt(with_tax(subtotal))
""",
    "sample_data.py": """def sample_items():
    return [(100, 2), (50, 1)]
""",
    "report.py": """import json

from invoices import invoice_total
from sample_data import sample_items

items = sample_items()
print(invoice_total(items))
print(json.dumps({"lines": len(items)}))
""",
}


def write_app(root):
    for rel, text in FILES.items():
        target = Path(root) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
```

## Complexity

O(total size of the sources) to write the files.

## Another way

For bug 2 you could also delay the import: put `from .totals import TAX_RATE` **inside** `with_tax`, so it
runs only when the function is called, long after both modules finished loading. That works, but it
hides the tangle instead of removing it. Moving the shared value is the cleaner design.
To find shadowing quickly, run `python -c "import json; print(json.__file__)"` in the folder.
