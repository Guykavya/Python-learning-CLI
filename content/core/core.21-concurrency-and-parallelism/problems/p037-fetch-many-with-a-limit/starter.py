import asyncio

import httpx


async def fetch_many(client: httpx.AsyncClient, urls: list[str], limit: int) -> dict[str, int]:
    """Return {url: status} for every url, with at most `limit` requests in flight."""
    statuses: dict[str, int] = {}
    # TODO: one coroutine per url, a shared asyncio.Semaphore(limit), asyncio.gather
    return statuses
