## Approach

Two opposite failure modes must both be avoided:

- **Crashing on one bad record.** The other 9,999 records are fine; one `null` must not cost the
  whole night's load. So each record is checked by a function that *returns* a reason instead of
  raising, and bad records are counted, not fatal.
- **Silently loading a broken batch.** If a fifth of the records fail, the source has probably
  changed. Loading the rest would publish wrong numbers that look plausible. So the batch is
  judged as a whole, and above the threshold **nothing** is written and the run fails loudly.

The order of the phases does the work: validate everything, decide, then write in one
transaction. Because nothing is written before the decision, "abort" needs no clean-up.

The summary is what an operator reads the next morning: how many, which reasons, and which
positions (so the records can be found in the quarantine file or the raw extract). The exception
carries the same summary, so the caller can log it before failing.

`duplicate id` is checked last and only against **accepted** ids: a rejected record never
"claims" its id, and a later valid record with the same id is the real one.

## Code

```python
def problem_with(record, seen_ids):
    if not isinstance(record, dict):
        return "not an object"
    id_ = record.get("id")
    if not isinstance(id_, int) or isinstance(id_, bool) or id_ <= 0:
        return "bad id"
    if record.get("status") not in STATUSES:
        return "bad status"
    amount = record.get("amount")
    if not isinstance(amount, str):
        return "bad amount"
    try:
        value = Decimal(amount)
    except InvalidOperation:
        return "bad amount"
    if not value.is_finite() or value < 0:
        return "bad amount"
    if id_ in seen_ids:
        return "duplicate id"
    return None


def load_with_threshold(conn, records, max_bad_ratio=0.1):
    good, failures, seen = [], [], set()
    for index, record in enumerate(records):
        reason = problem_with(record, seen)
        if reason is None:
            seen.add(record["id"])
            good.append({"id": record["id"], "status": record["status"], "amount": record["amount"]})
        else:
            failures.append((index, reason))
    total, bad = len(records), len(failures)
    summary = {"total": total, "loaded": 0, "bad": bad,
               "errors": dict(Counter(reason for _, reason in failures)), "failures": failures}
    if total and bad / total > max_bad_ratio:
        raise TooManyBadRecords(
            f"{bad} of {total} records are bad ({bad / total:.0%} > {max_bad_ratio:.0%})", summary)
    conn.execute(CREATE)
    with conn:
        conn.executemany(UPSERT, good)
    summary["loaded"] = len(good)
    return summary
```

## Complexity

O(n) time for n records. Memory O(n) for the good rows, because they are held until the
decision; for very large batches see below.

## Another way

For batches too big to hold in memory, write each record as it is checked **inside one open
transaction**, and at the end either `commit()` (below the threshold) or `rollback()` (above
it). SQLite then holds the pending rows instead of Python. Some teams also add a minimum batch
size before the ratio applies (1 bad record out of 3 is 33 %, but hardly an alarm), or combine a
ratio with an absolute limit ("more than 5 % **or** more than 1,000 bad records"). In a full
pipeline the bad records also go to a quarantine file with their reasons (p010), so they can be
fixed and replayed.
