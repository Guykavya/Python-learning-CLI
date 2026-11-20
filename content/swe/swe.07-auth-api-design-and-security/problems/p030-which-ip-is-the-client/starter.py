import ipaddress


def client_ip(remote_addr, x_forwarded_for=None, trusted_proxies=1):
    """Return the client's address, trusting only the last `trusted_proxies` hops of the chain."""
    return remote_addr          # TODO: read the header, count from the right
