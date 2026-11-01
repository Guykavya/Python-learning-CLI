import asyncio

import httpx


async def get_with_retry(client, url, retries=3, base_delay=0.1, sleep=asyncio.sleep):
    """GET url; retry 5xx and transport errors with exponential backoff; never retry 4xx."""
    raise NotImplementedError("loop over attempts; try the request; decide: return, raise or retry")
