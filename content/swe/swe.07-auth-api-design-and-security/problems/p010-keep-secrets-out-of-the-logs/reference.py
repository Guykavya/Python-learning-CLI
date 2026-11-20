import logging
import re

SENSITIVE = {"password", "token", "authorization", "api_key"}
MASK = "[REDACTED]"

_TEXT = re.compile(r"(?i)(?<!\w)(password|token|authorization|api_key)=(?:bearer\s+)?[^\s,&;]+")


def _clean(value):
    """Return a copy of `value` with sensitive dictionary values masked."""
    if isinstance(value, dict):
        return {key: MASK if str(key).lower() in SENSITIVE else _clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(_clean(item) for item in value)
    return value


class RedactSecrets(logging.Filter):
    """Mask secrets in every record before a handler writes it."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.args:
            record.args = _clean(record.args)
        message = record.getMessage()
        record.msg = _TEXT.sub(lambda m: m.group(1) + "=" + MASK, message)
        record.args = None
        return True
