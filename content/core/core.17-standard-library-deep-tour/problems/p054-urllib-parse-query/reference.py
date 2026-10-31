from urllib.parse import parse_qs, quote, urlencode, urlsplit

DEFAULT_PORTS = {"http": 80, "https": 443}


def build_url(base, params):
    if not params:
        return base
    return base + "?" + urlencode(params, doseq=True)


def parse_query(url):
    return parse_qs(urlsplit(url).query, keep_blank_values=True)


def host_port(url):
    parts = urlsplit(url)
    if not parts.hostname:
        raise ValueError(f"no host in {url!r}")
    port = parts.port
    if port is None:
        if parts.scheme not in DEFAULT_PORTS:
            raise ValueError(f"no port and unknown scheme {parts.scheme!r}")
        port = DEFAULT_PORTS[parts.scheme]
    return parts.hostname, port


def api_url(base, *segments):
    escaped = [quote(str(segment), safe="") for segment in segments]
    return "/".join([base.rstrip("/"), *escaped])
