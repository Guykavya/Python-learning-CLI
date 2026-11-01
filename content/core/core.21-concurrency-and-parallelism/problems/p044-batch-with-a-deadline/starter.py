import asyncio


async def gather_within(coro_fns, timeout):
    """Run all; after `timeout` return results in input order (exception objects for
    failures, None for unfinished calls); cancel the unfinished and wait for their cleanup."""
    raise NotImplementedError("create tasks, asyncio.wait with a timeout, cancel and await pending")
