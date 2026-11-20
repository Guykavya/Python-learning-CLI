import random
import time

import httpx


class RequestFailed(Exception):
    def __init__(self, message, status=None, attempts=1):
        super().__init__(message)
        self.status = status
        self.attempts = attempts


RETRY_STATUSES = {429, 502, 503, 504}
NEVER_SENT = (httpx.ConnectError, httpx.ConnectTimeout)
BASE, CAP, MAX_WAIT = 0.5, 8.0, 30.0


def _wait(attempt_index, response, rng):
    if response is not None:
        value = response.headers.get("retry-after", "").strip()
        if value.isascii() and value.isdigit():
            return min(float(value), MAX_WAIT)
    return rng.uniform(0, min(CAP, BASE * 2 ** attempt_index))


def _request(client, method, url, repeatable, attempts, sleep, rng, **kwargs):
    for attempt in range(attempts):
        last = attempt == attempts - 1
        response = None
        try:
            response = client.request(method, url, **kwargs)
        except httpx.TransportError as exc:
            retryable = isinstance(exc, NEVER_SENT) or (repeatable and isinstance(exc, (httpx.ReadTimeout, httpx.ReadError,
                                                                                         httpx.RemoteProtocolError)))
            if not retryable or last:
                raise RequestFailed(f"{method} {url} failed: {type(exc).__name__}", None, attempt + 1) from exc
        else:
            if response.status_code < 400:
                return response
            if response.status_code not in RETRY_STATUSES or not repeatable or last:
                raise RequestFailed(f"{method} {url} -> {response.status_code}", response.status_code, attempt + 1)
        sleep(_wait(attempt, response, rng))


def get_json(client, url, attempts=4, sleep=time.sleep, rng=random):
    response = _request(client, "GET", url, True, attempts, sleep, rng)
    try:
        return response.json()
    except ValueError:
        raise RequestFailed(f"GET {url}: the body is not JSON", response.status_code) from None


def post_json(client, url, payload, idempotency_key=None, attempts=4, sleep=time.sleep, rng=random):
    headers = {"Idempotency-Key": idempotency_key} if idempotency_key else {}
    response = _request(client, "POST", url, bool(idempotency_key), attempts, sleep, rng, json=payload, headers=headers)
    try:
        return response.json()
    except ValueError:
        raise RequestFailed(f"POST {url}: the body is not JSON", response.status_code) from None
