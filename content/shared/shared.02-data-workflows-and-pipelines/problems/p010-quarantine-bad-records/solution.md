## Approach

A helper decides about one record and returns either a row or a reason. The order of the
checks protects each step from the one before: `isinstance(record, dict)` first, because
`check` would crash on `None` or a string; `check` before `transform`, because a schema
error gives a clearer reason than the `KeyError` that `transform` would raise later.

`transform` is wrapped in `try`/`except Exception`. That is the right width: every normal
error (`KeyError`, `ValueError`, `decimal.InvalidOperation`, which is an `ArithmeticError` and
*not* a `ValueError`) is caught, but `KeyboardInterrupt` and `SystemExit`, which derive from
`BaseException` directly, still stop the program. The reason records the exception's class and
message, which is usually enough to find the problem without a traceback.

The quarantine is a JSON Lines file: one complete JSON object per line. You can append to it
forever, read it line by line, count it with `wc -l`, and re-process it later with the same
`process_batch` after fixing the transform. Each entry keeps the **original** record (so the
fix can be replayed) and the `run_id` (so you know which run produced it). The file is opened
in append mode and only when there is something to write, so a clean run leaves no empty file
that looks like trouble.

## Code

```python
import json
from pathlib import Path


def reason_for(record, check, transform):
    if not isinstance(record, dict):
        return None, "not an object"
    errors = check(record)
    if errors:
        return None, "; ".join(errors)
    try:
        return transform(record), None
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"


def process_batch(records, check, transform, quarantine_path, run_id):
    good, bad = [], []
    for record in records:
        row, reason = reason_for(record, check, transform)
        if reason is None:
            good.append(row)
        else:
            bad.append({"run_id": run_id, "reason": reason, "record": record})

    if bad:
        quarantine_path = Path(quarantine_path)
        quarantine_path.parent.mkdir(parents=True, exist_ok=True)
        with quarantine_path.open("a", encoding="utf-8") as f:
            for entry in bad:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {"good": good, "total": len(records), "ok": len(good), "quarantined": len(bad)}
```

## Complexity

O(n) calls of `check`/`transform` for `n` records; the file is opened once per batch.

## Another way

Write each bad record as soon as it is found (open the file lazily the first time). That uses
less memory for huge batches and keeps the quarantine even if the process is killed half way.
The next step, a **failure threshold** (abort the run if more than, say, 5 % of the records
are bad), is built on exactly these counts: `quarantined / total > 0.05` means something is
wrong with the source as a whole, not with one record.
