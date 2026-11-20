import random
import time

import httpx


class RequestFailed(Exception):
    def __init__(self, message, status=None, attempts=1):
        super().__init__(message)
        self.status = status
        self.attempts = attempts


def get_json(client, url, attempts=4, sleep=time.sleep, rng=random):
    # TODO: retry connect errors, read timeouts and 429/502/503/504; honour Retry-After; full-jitter backoff
    return client.get(url).json()


def post_json(client, url, payload, idempotency_key=None, attempts=4, sleep=time.sleep, rng=random):
    # TODO: like get_json, but only repeat the request when it carries an Idempotency-Key
    return client.post(url, json=payload).json()
