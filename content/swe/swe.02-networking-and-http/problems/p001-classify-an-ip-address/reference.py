import ipaddress


def classify(addr):
    if not isinstance(addr, str):
        return "invalid"
    try:
        ip = ipaddress.ip_address(addr)
    except ValueError:
        return "invalid"
    if ip.is_loopback:
        return "loopback"
    if ip.is_link_local:
        return "link-local"
    if ip.is_private:
        return "private"
    if ip.is_global and not ip.is_multicast:
        return "global"
    return "other"
