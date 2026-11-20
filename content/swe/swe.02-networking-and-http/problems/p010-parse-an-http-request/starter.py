from dataclasses import dataclass


class BadRequest(Exception):
    pass


class Headers:
    def __init__(self, pairs):
        self._pairs = list(pairs)

    # TODO: get, get_all, items, __contains__ (case-insensitive names)


@dataclass
class Request:
    method: str
    target: str
    version: str
    headers: Headers
    body: bytes


def parse_request(data):
    # TODO: cut at b"\r\n\r\n", parse the request line and the headers, read Content-Length bytes
    raise BadRequest("not implemented")
