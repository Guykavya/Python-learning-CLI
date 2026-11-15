import httpx


class NotJSONError(ValueError):
    """The server answered, but the body was not JSON."""


def get_json(client, path, params=None):
    """GET path; raise for 4xx/5xx; return None for 204; return parsed JSON or raise NotJSONError."""
    raise NotImplementedError("client.get(path, params=params), raise_for_status(), then response.json()")
