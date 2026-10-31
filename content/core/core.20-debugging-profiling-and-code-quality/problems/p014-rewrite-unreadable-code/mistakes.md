- "Improving" behaviour while refactoring, for example `row.strip().startswith("#")`. Now
  `" #x,1,2"` is skipped and the totals change. Refactoring must not change behaviour.
- Rounding each row's revenue. `0.004` three times totals `0.01` when rounded at the end, but
  `0.0` when rounded per row.
- Sorting by the unrounded revenue. `4.999` and `5.0` are equal after rounding and must then be
  ordered by name.
- `int(float(qty_text))` "to be safe". It accepts `"2.0"`, which the original skips.
- `except Exception:` or bare `except:`. The only error `int`/`float` raise on a string is
  `ValueError`; anything else is a bug you want to see.
- Using `csv.reader`. It handles quotes differently from `split(",")`, so `'"a,b",1,2'` would
  behave differently.
