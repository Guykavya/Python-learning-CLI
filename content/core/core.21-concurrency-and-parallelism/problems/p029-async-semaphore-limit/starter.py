import asyncio


async def run_limited(coro_fns, limit):
    """Run all coro_fns, at most `limit` at a time; results in input order."""
    # TODO: this starts everything at once and ignores limit.
    return list(await asyncio.gather(*(fn() for fn in coro_fns)))
