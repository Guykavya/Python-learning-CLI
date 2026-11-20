IDEMPOTENT = {"GET", "HEAD", "OPTIONS", "TRACE", "PUT", "DELETE"}
RETRY_STATUSES = {408, 429, 500, 502, 503, 504}


def worth_retrying(method, status, has_idempotency_key=False):
    # TODO: transient failure AND safe to repeat
    return False
