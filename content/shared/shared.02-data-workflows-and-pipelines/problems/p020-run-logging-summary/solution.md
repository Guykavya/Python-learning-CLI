## Approach

Good pipeline logs follow a few rules, and each one is in the code:

- **A run id on every line.** Several runs (yesterday's retry, today's schedule, a manual
  backfill) write to the same log. `grep a1b2c3d4` must pull out one run.
- **Levels mean something.** INFO for the start and the end of a run, WARNING for something a
  human may want to look at (a skipped record), ERROR when the run fails. Per-record detail is
  DEBUG, so it is off in production.
- **One summary line** with the numbers that matter (read, loaded, skipped, duration). It is the
  line dashboards and alerts are built on: "skipped > 0" or "loaded = 0" are cheap alarms.
- **Identifiers, not data.** A log line with the whole record would copy customer emails into
  every log file, log server and support ticket. The id is enough to look the record up in the
  quarantine or the source.
- **No `print`, no `basicConfig` in library code.** The application decides where logs go; a
  function only emits them.

`clock` is injected so the test can fix the duration; `run_id` is generated only when the caller
does not pass one (a scheduler usually passes its own).

## Code

```python
import logging
import time
import uuid
from decimal import Decimal, InvalidOperation

logger = logging.getLogger("pipeline")


def problem_with(record):
    id_ = record.get("id")
    if not isinstance(id_, int) or isinstance(id_, bool) or id_ <= 0:
        return "bad id"
    amount = record.get("amount")
    if not isinstance(amount, str):
        return "bad amount"
    try:
        value = Decimal(amount)
    except InvalidOperation:
        return "bad amount"
    if not value.is_finite() or value < 0:
        return "bad amount"
    return None


def process_batch(records, sink, *, run_id=None, clock=time.perf_counter):
    run_id = run_id or uuid.uuid4().hex[:8]
    start = clock()
    logger.info("run %s started: %d records", run_id, len(records))
    loaded = skipped = 0
    for record in records:
        reason = problem_with(record)
        if reason is not None:
            skipped += 1
            logger.warning("run %s skipped record id=%r: %s", run_id, record.get("id"), reason)
            continue
        try:
            sink(record)
        except Exception as error:
            logger.error("run %s failed after %d loaded: %s", run_id, loaded, type(error).__name__)
            raise
        loaded += 1
    duration = clock() - start
    logger.info("run %s finished: read=%d loaded=%d skipped=%d duration=%.3fs",
                run_id, len(records), loaded, skipped, duration)
    return {"run_id": run_id, "read": len(records), "loaded": loaded,
            "skipped": skipped, "duration": duration}
```

## Complexity

O(n) for n records; the log output is O(skipped + 2) lines instead of O(n).

## Another way

Put the run id into every record automatically with a `logging.LoggerAdapter`:
`log = logging.LoggerAdapter(logger, {"run_id": run_id})` and a formatter containing
`%(run_id)s`. Then the messages do not need to repeat it. Many teams also log the summary as one
JSON object (`logger.info(json.dumps(summary))`) so that a log system can parse the numbers.
The error line logs only the exception **class**: an exception message can itself contain data
(`ValueError: bad email asha@example.com`), so be careful before logging `str(error)`.
