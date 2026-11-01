import asyncio


async def fetch_all(names, fetch):
    """Fetch every name concurrently; return the results in input order."""
    return list(await asyncio.gather(*(fetch(name) for name in names)))
