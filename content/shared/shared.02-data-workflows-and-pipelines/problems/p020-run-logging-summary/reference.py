import logging
import time
import uuid
from decimal import Decimal, InvalidOperation

logger = logging.getLogger("pipeline")


def problem_with(record: dict) -> str | None:
    """The reason a record is invalid, or None if it is fine."""
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


def process_batch(records, sink, *, run_id=None, clock=time.perf_counter) -> dict:
    """Validate records, pass the good ones to sink, log a start line, skips and one summary."""
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
    return {"run_id": run_id, "read": len(records), "loaded": loaded, "skipped": skipped, "duration": duration}
