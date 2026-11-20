import logging
import re

SENSITIVE = {"password", "token", "authorization", "api_key"}
MASK = "[REDACTED]"


class RedactSecrets(logging.Filter):
    """Mask secrets in every record before a handler writes it."""

    def filter(self, record: logging.LogRecord) -> bool:
        # TODO: redact dict arguments (copies), redact name=value text, set record.msg and record.args = None
        return True
