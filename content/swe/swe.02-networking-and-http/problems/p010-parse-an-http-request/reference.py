from dataclasses import dataclass


class BadRequest(Exception):
    pass


class Headers:
    def __init__(self, pairs):
        self._pairs = list(pairs)

    def get(self, name, default=None):
        name = name.lower()
        for k, v in self._pairs:
            if k.lower() == name:
                return v
        return default

    def get_all(self, name):
        name = name.lower()
        return [v for k, v in self._pairs if k.lower() == name]

    def items(self):
        return list(self._pairs)

    def __contains__(self, name):
        return self.get(name) is not None


@dataclass
class Request:
    method: str
    target: str
    version: str
    headers: Headers
    body: bytes


def parse_request(data):
    head, sep, rest = data.partition(b"\r\n\r\n")
    if not sep:
        raise BadRequest("the blank line that ends the headers is missing")
    lines = head.decode("latin-1").split("\r\n")
    parts = lines[0].split(" ")
    if len(parts) != 3 or not parts[0] or not parts[1] or not parts[2].startswith("HTTP/"):
        raise BadRequest("malformed request line")
    method, target, version = parts
    pairs = []
    for line in lines[1:]:
        name, colon, value = line.partition(":")
        if not colon or not name or name != name.strip():
            raise BadRequest(f"malformed header line: {line!r}")
        pairs.append((name, value.strip()))
    headers = Headers(pairs)
    if version == "HTTP/1.1" and "host" not in headers:
        raise BadRequest("HTTP/1.1 requests need a Host header")
    lengths = set(headers.get_all("content-length"))
    length = 0
    if lengths:
        if len(lengths) > 1:
            raise BadRequest("conflicting Content-Length headers")
        text = lengths.pop()
        if not (text.isascii() and text.isdigit()):
            raise BadRequest("Content-Length is not a number")
        length = int(text)
    body = rest[:length]
    if len(body) < length:
        raise BadRequest("body cut short")
    return Request(method, target, version, headers, body)
