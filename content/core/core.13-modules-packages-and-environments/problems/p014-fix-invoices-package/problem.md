# Fix: the invoices package that will not import

Arjun split his billing script into a small package. `write_app(root)` in the starter writes his project
into the folder `root`:

```text
root/
├── report.py          the program you run:  python report.py
├── json.py            his helper with the sample data
└── invoices/
    ├── __init__.py    re-exports invoice_total
    ├── money.py       fmt(amount) and with_tax(amount)
    └── totals.py      invoice_total(items) and TAX_RATE = 0.18
```

What it should do:

- `invoices.invoice_total(items)` takes `(price, quantity)` pairs, adds 18% tax and returns the total as
  text: `invoice_total([(100, 2), (50, 1)])` → `"Rs 295.00"`.
- `invoices.money.fmt(295)` → `"Rs 295.00"` and `invoices.money.with_tax(100)` → `118.0` (about).
- `python report.py`, run inside `root`, prints exactly:

```text
Rs 295.00
{"lines": 2}
```

**This package has bugs. Find and fix them.** Right now `import invoices` fails, and once that is fixed it
fails in a different way. Even then, `python report.py` crashes with an `AttributeError` about `json`.
There are **three** bugs: one is in how `totals.py` imports `money`, one is a circular import between
`money.py` and `totals.py`, and one is a file name.

Copy the starter into `solution.py` and fix the **source text** in `FILES` (you may rename, add or remove
files). Keep the function `write_app(root)`, and keep `report.py`, `invoices.invoice_total`,
`invoices.money.fmt` and `invoices.money.with_tax` working as described.

To see the errors yourself, call `write_app("scratch")` from a small script, then run
`python report.py` inside `scratch/`.
