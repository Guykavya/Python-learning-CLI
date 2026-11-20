import ipaddress


def client_ip(remote_addr, x_forwarded_for=None, trusted_proxies=1):
    if trusted_proxies <= 0 or not x_forwarded_for:
        return remote_addr                                         # no trusted proxy: the header is just user input
    chain = [part.strip() for part in x_forwarded_for.split(",")] + [remote_addr]
    if len(chain) < trusted_proxies + 1:
        return remote_addr                                         # the request did not pass through all our proxies
    candidate = chain[-(trusted_proxies + 1)]
    try:
        ipaddress.ip_address(candidate)
    except ValueError:
        return remote_addr                                         # garbage such as "unknown"
    return candidate
