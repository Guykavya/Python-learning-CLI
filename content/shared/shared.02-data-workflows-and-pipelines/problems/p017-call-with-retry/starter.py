import logging
import random
import time

import httpx

logger = logging.getLogger("pipeline")


def call_with_retry(client, path, params=None, *, max_attempts=4, base_delay=1.0,
                    max_delay=30.0, sleep=time.sleep, rand=random.random):
    """GET path and return its JSON; retry 429, 5xx and transport errors with backoff."""
    raise NotImplementedError("for attempt 1..max_attempts: try -> return | raise | log, sleep(delay), loop")
