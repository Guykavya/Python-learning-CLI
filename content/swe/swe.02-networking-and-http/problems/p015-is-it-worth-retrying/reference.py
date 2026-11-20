IDEMPOTENT = {"GET", "HEAD", "OPTIONS", "TRACE", "PUT", "DELETE"}
RETRY_STATUSES = {408, 429, 500, 502, 503, 504}


def worth_retrying(method, status, has_idempotency_key=False):
    safe_to_repeat = method.upper() in IDEMPOTENT or has_idempotency_key
    if status is None:                      # connection error: the request may or may not have been processed
        return safe_to_repeat
    if status in RETRY_STATUSES:
        return safe_to_repeat
    return False
