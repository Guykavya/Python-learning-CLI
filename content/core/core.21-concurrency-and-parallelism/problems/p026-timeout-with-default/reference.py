import asyncio


async def with_timeout(coro_fn, seconds, default):
    """Await coro_fn(); return default if it takes longer than seconds."""
    try:
        async with asyncio.timeout(seconds):
            return await coro_fn()
    except TimeoutError:
        return default
