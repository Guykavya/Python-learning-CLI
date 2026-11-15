import logging
import random
import time

import httpx

logger = logging.getLogger("pipeline")


def retry_after_seconds(response: httpx.Response | None) -> int | None:
    """Retry-After as whole seconds, or None when absent or not a plain number."""
    if response is None:
        return None
    value = response.headers.get("Retry-After", "").strip()
    return int(value) if value.isdigit() else None


def call_with_retry(client, path, params=None, *, max_attempts=4, base_delay=1.0,
                    max_delay=30.0, sleep=time.sleep, rand=random.random):
    """GET path and return its JSON; retry 429, 5xx and transport errors with backoff."""
    for attempt in range(1, max_attempts + 1):
        response = None
        try:
            response = client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as error:
            status = error.response.status_code
            if status != 429 and status < 500:
                raise                                  # 4xx: our request is wrong; retrying cannot help
            if attempt == max_attempts:
                raise
            reason = str(status)
        except httpx.TransportError as error:
            if attempt == max_attempts:
                raise
            reason = type(error).__name__

        wait = retry_after_seconds(response)
        if wait is not None:
            delay = float(min(wait, max_delay))        # the server told us; obey it exactly
        else:
            backoff = min(max_delay, base_delay * 2 ** (attempt - 1))
            delay = backoff / 2 + rand() * backoff / 2
        logger.warning("attempt %d failed (%s), retrying in %.2fs", attempt, reason, delay)
        sleep(delay)
