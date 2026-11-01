import asyncio

import httpx


async def fetch_many(client: httpx.AsyncClient, urls: list[str], limit: int) -> dict[str, int]:
    """Return {url: status} for every url, with at most `limit` requests in flight."""
    semaphore = asyncio.Semaphore(limit)

    async def status_of(url: str) -> int:
        async with semaphore:          # wait for a free slot, give it back on exit
            response = await client.get(url)
            return response.status_code

    codes = await asyncio.gather(*(status_of(url) for url in urls))
    return dict(zip(urls, codes))
