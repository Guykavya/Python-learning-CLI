import httpx


async def get_json(client: httpx.AsyncClient, url: str) -> dict:
    """GET url with client; raise httpx.HTTPStatusError for 4xx/5xx; return the JSON body."""
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
