## Approach

```python
DEFAULT_PORTS = {"http": 80, "https": 443}


def split_hostport(text, scheme="http"):
    port_text = None
    if text.startswith("["):
        end = text.find("]")
        if end == -1:
            raise ValueError("missing ']'")
        host = text[1:end]
        rest = text[end + 1:]
        if rest:
            if not rest.startswith(":"):
                raise ValueError("garbage after ']'")
            port_text = rest[1:]
    else:
        if text.count(":") > 1:
            raise ValueError("IPv6 addresses need square brackets")
        host, colon, port_text = text.partition(":")
        if not colon:
            port_text = None
    if not host:
        raise ValueError("empty host")
    if port_text is None:
        if scheme not in DEFAULT_PORTS:
            raise ValueError(f"no default port for scheme {scheme!r}")
        return host, DEFAULT_PORTS[scheme]
    if not (port_text.isascii() and port_text.isdigit()):
        raise ValueError(f"bad port {port_text!r}")
    port = int(port_text)
    if not 1 <= port <= 65535:
        raise ValueError(f"port out of range: {port}")
    return host, port
```

The brackets exist because an IPv6 address is full of colons: without them, `2001:db8::1:80` could be an address, or an address and a port. `isascii()` is needed because `str.isdigit()` is also true for other digit characters such as Arabic-Indic digits, which `int()` would accept silently.

Example: `"[::1]:443"`: `end = 3`, host `"::1"`, `rest = ":443"`, port text `"443"`, so `("::1", 443)`.

## Complexity

`O(len(text))`.

## Another way

`urllib.parse.urlsplit("//" + text)` has `.hostname` and `.port`. It strips the brackets, and `.port` raises `ValueError` on a bad port, so for many uses it is enough. Writing it by hand shows the rules.

## Why it matters

Every HTTP client does this before it opens a socket (chapter sections 3.2 and 13.1). A bad parse sends the request to the wrong place.
