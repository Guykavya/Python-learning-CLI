## Hint 1

You cannot know whether the batch is "too bad" until you have checked **every** record. So
what is the earliest moment at which you may write anything to the database? Split the work
into three phases: check all, decide, write.

For the checks: what is the smallest function that turns one record into either `None` (fine)
or a reason string, and never raises? Which test must come first so that `record.get(...)` is
safe to call?

## Hint 2

```
good, failures, seen = [], [], set()
for index, record in enumerate(records):
    reason = problem_with(record, seen)     # not dict / bad id / bad status / bad amount / duplicate id
    if reason is None: seen.add(record["id"]); good.append(row)
    else: failures.append((index, reason))
summary = {"total", "loaded": 0, "bad", "errors": Counter of reasons as a dict, "failures"}
if total and bad / total > max_bad_ratio:
    raise TooManyBadRecords(f"{bad} of {total} records are bad (...)", summary)
CREATE TABLE IF NOT EXISTS ...
with conn: executemany(UPSERT, good)
summary["loaded"] = len(good); return summary
```

`isinstance(True, int)` is `True`; `Decimal("ten")` raises `decimal.InvalidOperation`.
