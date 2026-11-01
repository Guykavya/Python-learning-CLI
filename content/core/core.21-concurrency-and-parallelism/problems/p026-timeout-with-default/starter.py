import asyncio


async def with_timeout(coro_fn, seconds, default):
    """Await coro_fn(); return default if it takes longer than seconds."""
    # TODO: there is no time limit at all yet.
    return await coro_fn()
