import logging
import time
import uuid
from decimal import Decimal, InvalidOperation

logger = logging.getLogger("pipeline")


def process_batch(records, sink, *, run_id=None, clock=time.perf_counter) -> dict:
    """Validate records, pass the good ones to sink, log a start line, skips and one summary."""
    raise NotImplementedError("run id, clock(), INFO start, WARNING per skip, sink(good), INFO summary")
