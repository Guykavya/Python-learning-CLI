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
