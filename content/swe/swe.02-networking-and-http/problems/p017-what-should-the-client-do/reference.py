import math
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FIX = {400, 404, 405, 409, 410, 415, 422}
RETRY = {408, 500, 502, 504}
REDIRECTS = {301, 302, 303, 307, 308}


def _retry_after(value, now):
    value = value.strip()
    if value.isascii() and value.isdigit():
        return int(value)
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0, math.ceil((when - now).total_seconds()))


def client_action(status, headers, now=None):
    headers = {k.lower(): v for k, v in headers.items()}
    if now is None:
        now = datetime.now(timezone.utc)
    if 200 <= status < 300 or status == 304:
        return "use"
    if status in REDIRECTS:
        location = headers.get("location")
        return f"follow:{location}" if location else "give-up"
    if status in (429, 503):
        seconds = _retry_after(headers["retry-after"], now) if "retry-after" in headers else None
        return f"wait:{seconds}" if seconds is not None else "retry"
    if status in RETRY:
        return "retry"
    if status == 401:
        return "log-in"
    if status in FIX:
        return "fix-request"
    return "give-up"
