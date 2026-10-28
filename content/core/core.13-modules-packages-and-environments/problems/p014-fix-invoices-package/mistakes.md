- Fixing bug 1 by adding `invoices/` to `sys.path`. Then `money` exists twice (as `money` and as
  `invoices.money`), with two separate copies of its state.
- Swapping the two import lines in `totals.py` (putting `TAX_RATE = 0.18` first). It happens to work
  here, but the cycle is still there and breaks again when someone reorders the lines or imports
  `money` first.
- Fixing the circular import with `import invoices.totals` at the top of `money.py` and then using
  `invoices.totals.TAX_RATE` at module level. The value still does not exist yet during loading.
- Renaming `json.py` but still calling `json.sample_items()` in `report.py`. Import the helper by its new name.
- Renaming it to another standard library name. `data.py` is fine; `types.py`, `email.py`, `random.py`
  or `test.py` would hide a real module again.
- Reading only the first line of a traceback. The useful line is usually the **last** one.
