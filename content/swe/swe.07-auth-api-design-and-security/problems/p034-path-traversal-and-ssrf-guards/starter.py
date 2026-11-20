import ipaddress
from pathlib import Path
from urllib.parse import urlparse


class UnsafeURL(ValueError):
    """The URL must not be fetched."""


def safe_join(base, user_path):
    """Return the resolved path inside base, or raise PermissionError."""
    return Path(base) / user_path          # TODO: resolve, then check that it stays inside base


def check_url(url, resolve):
    """Return the list of approved IP addresses, or raise UnsafeURL."""
    return []                              # TODO: scheme, host, resolve, check every address
