# Quarantine bad records instead of crashing

One order out of 20,000 has the amount `"12,00"` (a comma instead of a dot). If the pipeline
crashes on it, 19,999 good orders are not loaded either, and someone gets woken up at 3 am. If
the pipeline silently skips it, the order is lost and nobody ever knows. The good middle way
is a **quarantine**: put the bad record, with the reason, in a separate file, load the rest,
and report how many were set aside.

Write

```python
def process_batch(records, check, transform, quarantine_path, run_id):
```

- `records`: a list of raw records as they came from the API (normally dicts, but a broken
  source can send anything, for example `null` or a string).
- `check(record)`: returns a list of error strings (`[]` = fine), like `check_schema`.
- `transform(record)`: returns the clean row, or **raises** an exception (any `Exception`
  subclass: `KeyError`, `ValueError`, `decimal.InvalidOperation`, ...).
- `quarantine_path`: a `pathlib.Path` to a **JSON Lines** file (one JSON object per line).
- `run_id`: a string that identifies this run.

For each record, in order:

1. If it is not a `dict`, it is bad with the reason `"not an object"`.
2. Otherwise call `check(record)`. If it returns errors, the record is bad with the reason
   `"; ".join(errors)`. Do **not** call `transform` for it.
3. Otherwise call `transform(record)`. If it raises an `Exception`, the record is bad with the
   reason `f"{type(error).__name__}: {error}"`. If it works, keep the returned row.

Every bad record becomes one line in the quarantine file:

```json
{"run_id": "run-7", "reason": "amount: missing", "record": {"id": 5, "status": "shipped"}}
```

- `"record"` is the original record, unchanged.
- **Append** to the file (a quarantine collects bad records from many runs). Create the parent
  folder if needed. Write with `encoding="utf-8"`.
- If there are no bad records, do not create the file at all.
- Catch `Exception`, never a bare `except:` or `BaseException`: Ctrl+C (`KeyboardInterrupt`)
  must still stop the program.

Return

```python
{"good": [row, row, ...], "total": n, "ok": number_good, "quarantined": number_bad}
```

**Example**

```python
records = [{"id": 1, "amount": "10.00"}, {"id": 2}, "oops", {"id": 3, "amount": "12,00"}]
result = process_batch(records, check, transform, Path("q/orders.jsonl"), "run-7")
result["ok"], result["quarantined"], result["total"]   # (1, 3, 4)
```

`q/orders.jsonl` now ends with three lines; their reasons are `"amount: missing"`,
`"not an object"` and `"InvalidOperation: [<class 'decimal.ConversionSyntax'>]"`.
