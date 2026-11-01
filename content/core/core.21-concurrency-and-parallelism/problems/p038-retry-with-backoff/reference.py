import asyncio

import httpx


async def get_with_retry(client, url, retries=3, base_delay=0.1, sleep=asyncio.sleep):
    """GET url; retry 5xx and transport errors with exponential backoff; never retry 4xx."""
    for attempt in range(retries + 1):
        last = attempt == retries
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as error:
            if error.response.status_code < 500 or last:
                raise                      # 4xx is permanent; or no attempts left
        except httpx.TransportError:
            if last:
                raise
        await sleep(base_delay * 2**attempt)
