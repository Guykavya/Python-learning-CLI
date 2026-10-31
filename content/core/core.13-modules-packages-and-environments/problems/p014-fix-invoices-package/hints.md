## Hint 1

Run it and read each error **completely**, from the last line up. `No module named 'money'`: which folders
does Python search for a top-level module called `money`? Is the `invoices` folder one of them? What does
a leading dot in `from .money import ...` mean?

## Hint 2

After the first fix you get `cannot import name 'TAX_RATE' from partially initialized module`. Follow the
order: `__init__` imports `totals` → `totals` imports `money` (first line, before `TAX_RATE = 0.18` runs)
→ `money` imports `TAX_RATE` from `totals`, which is only half done. How can you make the arrows point
one way only? Where should a value live that both modules need?

## Hint 3

The third error: `module 'json' has no attribute 'dumps'`. Which `json` did `import json` load? Think
of `sys.path[0]` when you run `python report.py`.

## Hint 4

```
money.py:   TAX_RATE = 0.18  (moved here, no import from totals)
            def fmt ..., def with_tax ...
totals.py:  from .money import fmt, with_tax
            def invoice_total ...
json.py  →  rename to sample_data.py
report.py:  import json
            from invoices import invoice_total
            from sample_data import sample_items
            items = sample_items() ...
```
