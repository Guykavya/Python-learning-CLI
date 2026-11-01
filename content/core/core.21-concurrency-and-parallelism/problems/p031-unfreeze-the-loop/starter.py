import asyncio


async def handle_all(requests, slow_lookup):
    """Run the blocking slow_lookup for every request without freezing the loop."""
    # TODO: slow_lookup blocks, so this freezes the event loop and runs
    # the lookups one by one.
    return [slow_lookup(r) for r in requests]
