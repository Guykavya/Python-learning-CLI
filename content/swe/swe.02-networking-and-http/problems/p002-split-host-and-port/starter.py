DEFAULT_PORTS = {"http": 80, "https": 443}


def split_hostport(text, scheme="http"):
    # TODO: bracketed IPv6 first, then host[:port]; validate the port and the host
    return text, 80
