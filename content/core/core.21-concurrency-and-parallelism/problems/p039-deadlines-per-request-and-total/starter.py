import asyncio

import httpx


async def fetch_with_deadlines(client: httpx.AsyncClient, urls: list[str],
                               per_request: float, total: float) -> dict:
    """Return {url: text or "timeout"}; each request <= per_request s, whole call <= total s."""
    raise NotImplementedError("one task per url with asyncio.timeout(per_request) inside, "
                              "all of them under asyncio.timeout(total)")
