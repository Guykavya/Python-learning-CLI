import asyncio


async def handle_all(requests, slow_lookup):
    """Run the blocking slow_lookup for every request without freezing the loop."""
    return list(
        await asyncio.gather(*(asyncio.to_thread(slow_lookup, r) for r in requests))
    )
