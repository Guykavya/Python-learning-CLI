## Approach

```python
IDEMPOTENT = {"GET", "HEAD", "OPTIONS", "TRACE", "PUT", "DELETE"}
RETRY_STATUSES = {408, 429, 500, 502, 503, 504}


def worth_retrying(method, status, has_idempotency_key=False):
    safe_to_repeat = method.upper() in IDEMPOTENT or has_idempotency_key
    if status is None:                      # connection error: the request may or may not have been processed
        return safe_to_repeat
    if status in RETRY_STATUSES:
        return safe_to_repeat
    return False
```

The two conditions are independent. A `404` is never transient: the server answered clearly, and repeating gives the same answer. A `POST` that timed out may have been processed (the reply was lost), so repeating it can create a duplicate unless an idempotency key lets the server recognise the repeat (chapter section 21.5). `PUT` and `DELETE` are idempotent by definition: doing them twice leaves the same state.

Example: `worth_retrying("DELETE", None)`: `DELETE` is idempotent, `None` is a connection error: `True`.

## Complexity

`O(1)`.

## Another way

Connection errors that happen **before** the request is sent (connect refused) are safe to retry for any method; this function does not know that, so it takes the cautious view for `None`. A real client distinguishes the error types (problem 30).

## Why it matters

Blind retries cause double payments and duplicate orders. This one small function is the rule that prevents it.
