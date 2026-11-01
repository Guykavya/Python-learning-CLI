import asyncio


async def run_limited(coro_fns, limit):
    """Run all coro_fns, at most `limit` at a time; results in input order."""
    if limit < 1:
        raise ValueError(f"limit must be at least 1, got {limit}")
    sem = asyncio.Semaphore(limit)

    async def one(fn):
        async with sem:
            return await fn()

    return list(await asyncio.gather(*(one(fn) for fn in coro_fns)))
