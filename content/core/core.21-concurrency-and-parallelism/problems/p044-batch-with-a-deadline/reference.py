import asyncio


async def gather_within(coro_fns, timeout):
    """Run all; after `timeout` return results in input order (exception objects for
    failures, None for unfinished calls); cancel the unfinished and wait for their cleanup."""
    if not coro_fns:
        return []                       # asyncio.wait() refuses an empty collection
    tasks = [asyncio.create_task(fn()) for fn in coro_fns]
    done, pending = await asyncio.wait(tasks, timeout=timeout)
    for task in pending:
        task.cancel()
    # wait until every cancelled task has really finished (its finally blocks have run)
    await asyncio.gather(*pending, return_exceptions=True)

    results = []
    for task in tasks:
        if task not in done:
            results.append(None)
        elif task.exception() is not None:
            results.append(task.exception())
        else:
            results.append(task.result())
    return results
