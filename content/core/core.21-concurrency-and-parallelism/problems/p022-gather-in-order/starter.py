import asyncio


async def fetch_all(names, fetch):
    """Fetch every name concurrently; return the results in input order."""
    # TODO: this waits for each fetch before starting the next one,
    # so the total time is the SUM of all fetches. Use asyncio.gather.
    results = []
    for name in names:
        results.append(await fetch(name))
    return results
