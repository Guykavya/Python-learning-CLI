import asyncio

import httpx


async def fetch_with_deadlines(client: httpx.AsyncClient, urls: list[str],
                               per_request: float, total: float) -> dict:
    """Return {url: text or "timeout"}; each request <= per_request s, whole call <= total s."""
    results = {url: "timeout" for url in urls}   # the default for anything that never finishes

    async def fetch_one(url: str) -> None:
        try:
            async with asyncio.timeout(per_request):
                response = await client.get(url)
        except TimeoutError:
            return                                # stays "timeout"
        results[url] = response.text

    try:
        async with asyncio.timeout(total):
            async with asyncio.TaskGroup() as group:
                for url in urls:
                    group.create_task(fetch_one(url))
    except TimeoutError:
        pass   # TaskGroup has already cancelled AND awaited every unfinished task
    return results
