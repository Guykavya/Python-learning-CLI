import httpx


class NotJSONError(ValueError):
    """The server answered, but the body was not JSON."""


def get_json(client, path, params=None):
    """GET path; raise for 4xx/5xx; return None for 204; return parsed JSON or raise NotJSONError."""
    response = client.get(path, params=params)
    response.raise_for_status()              # 4xx/5xx -> httpx.HTTPStatusError
    if response.status_code == 204:
        return None
    try:
        return response.json()
    except ValueError as error:              # json.JSONDecodeError is a ValueError
        snippet = response.text[:80]
        raise NotJSONError(
            f"{path} did not return JSON (status {response.status_code}): {snippet!r}"
        ) from error
