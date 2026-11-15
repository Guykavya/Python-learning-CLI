## Hint 1

Separate the two jobs. First write `problem_with(record) -> str | None` that returns `"bad id"`,
`"bad amount"` or `None`. Then the main loop only counts and logs. Which three log calls does a
normal run make in total if no record is bad? What exactly may appear in a WARNING line, and
what may not?

Remember: `isinstance(True, int)` is `True` in Python, and `Decimal("abc")` raises
`decimal.InvalidOperation`.

## Hint 2

```
logger = logging.getLogger("pipeline")          # at module level

run_id = run_id or uuid.uuid4().hex[:8]
start = clock()
logger.info("run %s started: %d records", run_id, len(records))
for record in records:
    reason = problem_with(record)
    if reason: skipped += 1; logger.warning("run %s skipped record id=%r: %s", run_id, record.get("id"), reason); continue
    try: sink(record)
    except Exception as e: logger.error("run %s failed after %d loaded: %s", run_id, loaded, type(e).__name__); raise
    loaded += 1
duration = clock() - start
logger.info("run %s finished: read=%d loaded=%d skipped=%d duration=%.3fs", ...)
return {...}
```
