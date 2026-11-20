from urllib.parse import quote, urlencode


def build_url(base, segments, query=None):
    url = base.rstrip("/")
    for segment in segments:
        url += "/" + quote(str(segment), safe="")
    if query:
        pairs = {k: v for k, v in query.items() if v is not None}
        text = urlencode(pairs, doseq=True)
        if text:
            url += "?" + text
    return url
