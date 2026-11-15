# Run logging: run id, counts and one summary line

At 3 a.m. nobody is watching the pipeline. The next morning the logs are all you have, so they
must answer: *which run was this, how much did it read, load and skip, how long did it take, did
it finish?* And they must not leak customer data: logs are copied to many systems and read by
many people.

Write

```python
def process_batch(records, sink, *, run_id=None, clock=time.perf_counter) -> dict:
```

- Use the logger `logging.getLogger("pipeline")`. Never `print`. Do not call
  `logging.basicConfig` (configuring handlers is the job of the program's entry point).
- `run_id`: use the given one; if it is `None`, make one with `uuid.uuid4().hex[:8]`
  (`import uuid`), so every run has its own id. Every log line of the run contains it.
- Call `clock()` exactly twice: once at the start, once at the end. `duration` is the difference.
- Log at **INFO**, exactly:
  `run <run_id> started: <n> records`
- Check each record; a record is valid when:
  - its `"id"` is an `int` (not a `bool`) greater than 0, otherwise the reason is `bad id`;
  - its `"amount"` is a string that `Decimal` can parse and is not negative, otherwise the
    reason is `bad amount` (check the id first).
- For a valid record call `sink(record)`. For an invalid one log a **WARNING**:
  `run <run_id> skipped record id=<repr of the id>: <reason>`, for example
  `run a1b2c3d4 skipped record id=103: bad amount`. Log **only** the id and the reason, never the
  record itself: it contains the customer's email.
- At the end log at **INFO**, exactly one line:
  `run <run_id> finished: read=<n> loaded=<k> skipped=<s> duration=<seconds with 3 decimals>s`
  There are no other INFO lines (no INFO per record: a run of a million records must not write a
  million INFO lines; use DEBUG for that if you want).
- If `sink` raises, log an **ERROR** `run <run_id> failed after <k> loaded: <exception class name>`
  and re-raise the exception. No "finished" line in that case.
- Return `{"run_id": ..., "read": n, "loaded": k, "skipped": s, "duration": seconds}`.

Write the log calls with `%`-style arguments, `logger.info("run %s started: %d records", run_id, n)`:
the message is only formatted if the line is really emitted.

**Example**

```python
records = [
    {"id": 101, "customer": {"email": "asha@example.com"}, "amount": "19.99"},
    {"id": 102, "customer": {"email": "ravi@example.com"}, "amount": "-5"},
    {"id": "103", "customer": {"email": "meera@example.com"}, "amount": "7.00"},
]
times = iter([100.0, 100.25])
process_batch(records, loaded.append, run_id="a1b2c3d4", clock=lambda: next(times))
# {'run_id': 'a1b2c3d4', 'read': 3, 'loaded': 1, 'skipped': 2, 'duration': 0.25}
```

Logged:

```
INFO    run a1b2c3d4 started: 3 records
WARNING run a1b2c3d4 skipped record id=102: bad amount
WARNING run a1b2c3d4 skipped record id='103': bad id
INFO    run a1b2c3d4 finished: read=3 loaded=1 skipped=2 duration=0.250s
```
