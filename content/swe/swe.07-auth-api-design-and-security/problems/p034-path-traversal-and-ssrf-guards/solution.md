## Approach

```python
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
```

**Why resolve the path first.** `"..." in name` is a block-list: it misses absolute paths and symlinks. `resolve()` gives the real, final path; the comparison is then about the thing that will be opened. `is_relative_to` compares path *parts*, so `/srv/uploads-evil` is not inside `/srv/uploads`, which a string `startswith("/srv/uploads")` would get wrong. Resolving `base` too matters when the base itself sits behind a symlink (for example `/tmp` on macOS).

**Why resolve the host first.** The same logic as the path: check what you will really use. A text check on the URL cannot see that `localtest.example` points to `127.0.0.1`, or that `2130706433` is `127.0.0.1` for the operating system. After the check, the caller should connect to the **returned address**, not resolve the name a second time, otherwise DNS can answer differently (DNS rebinding, chapter 14.6). The rest of the defence (no blind redirects, timeouts, a network segment) is in the chapter.

`is_global` is `False` for loopback, private ranges, link-local (including the cloud metadata address `169.254.169.254`), the carrier-grade NAT range and unspecified addresses, so one property covers the whole list.

## Complexity

`safe_join` costs one path resolution (a few system calls per path part). `check_url` does one resolver call and O(number of addresses) checks.

## Another way

Skip the clever check: use an **allow-list** of file ids and hosts. Store uploads under a generated name (`uuid4().hex`) and look them up by id, so the client never sends a path; for webhooks, let customers register a host once and compare the URL's host with a short list. A block-list of bad addresses is the last line of defence, not the first.
