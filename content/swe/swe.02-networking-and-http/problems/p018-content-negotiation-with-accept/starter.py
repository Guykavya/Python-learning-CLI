def choose(accept_header, offered):
    # TODO: parse the ranges; most specific match gives the q; highest q wins; ties keep the server's order
    return offered[0] if offered else None
