- Writing each good record as soon as it passes, then raising at the end. The "aborted" batch
  is already half in the table, which is exactly the silent damage the threshold should prevent.
- `>=` instead of `>`. With `max_bad_ratio=0.1`, 1 bad record in 10 is allowed.
- Dividing by zero on an empty batch.
- Letting the checks raise (`record["id"]` on `None`, `Decimal("ten")`, `"x" < 0`) and wrapping
  the loop in `try/except Exception: continue`. It works until the bug is in *your* code; then
  every record is "bad" for the wrong reason. Return reasons explicitly.
- Checking `record.get("id")` before checking that the record is a dict: `None.get` raises.
- Treating `True` as a valid id, or accepting `9.5` (a float) as an amount: money must stay a string
  or `Decimal`, never a float.
- Counting a duplicate against **every** earlier record, including rejected ones.
- Raising a plain `ValueError("too many bad records")` without the counts. The operator then has
  to re-run the job with extra logging to find out what went wrong.
