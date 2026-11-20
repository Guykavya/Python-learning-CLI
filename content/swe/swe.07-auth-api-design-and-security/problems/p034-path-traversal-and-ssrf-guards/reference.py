import ipaddress
from pathlib import Path
from urllib.parse import urlparse


class UnsafeURL(ValueError):
    pass


def safe_join(base, user_path):
    if "\0" in user_path:
        raise PermissionError("NUL character in the path")
    root = Path(base).resolve()
    target = (root / user_path).resolve()                 # removes .. and follows symlinks
    if not target.is_relative_to(root):                    # a path-aware check, not startswith
        raise PermissionError("path escapes the base folder")
    return target


def check_url(url, resolve):
    parts = urlparse(url)
    if parts.scheme not in ("http", "https"):
        raise UnsafeURL("only http and https are allowed")
    host = parts.hostname
    if not host:
        raise UnsafeURL("the URL has no host")
    try:
        ipaddress.ip_address(host)
        addresses = [host]                                  # already an address: nothing to resolve
    except ValueError:
        try:
            addresses = list(resolve(host))                 # resolve FIRST ...
        except OSError as exc:
            raise UnsafeURL("the host does not resolve") from exc
        if not addresses:
            raise UnsafeURL("the host does not resolve")
    for text in addresses:                                  # ... then check EVERY address
        try:
            ip = ipaddress.ip_address(text)
        except ValueError as exc:
            raise UnsafeURL(f"not an IP address: {text!r}") from exc
        if ip.version == 6 and ip.ipv4_mapped:
            ip = ip.ipv4_mapped                             # ::ffff:127.0.0.1 is really 127.0.0.1
        if not ip.is_global:
            raise UnsafeURL(f"{ip} is not a public address")
    return addresses
