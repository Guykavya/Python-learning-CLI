import asyncio

_DONE = object()      # sentinel: "no more items", one per consumer


async def produce_consume(items, consume, maxsize, n_consumers):
    """Feed items through a bounded queue to n_consumers; return results in item order."""
    queue = asyncio.Queue(maxsize=maxsize)
    results = {}

    async def producer():
        for index, item in enumerate(items):      # lazy: pulls one item at a time
            await queue.put((index, item))        # waits while the queue is full
        for _ in range(n_consumers):
            await queue.put(_DONE)

    async def consumer():
        while True:
            entry = await queue.get()
            if entry is _DONE:
                return
            index, item = entry
            results[index] = await consume(item)

    async with asyncio.TaskGroup() as group:
        group.create_task(producer())
        for _ in range(n_consumers):
            group.create_task(consumer())
    return [results[i] for i in range(len(results))]
