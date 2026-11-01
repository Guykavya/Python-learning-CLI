import httpx


async def get_json(client: httpx.AsyncClient, url: str) -> dict:
    """GET url with client; raise httpx.HTTPStatusError for 4xx/5xx; return the JSON body."""
    raise NotImplementedError("send the request with client.get, check the status, return .json()")
