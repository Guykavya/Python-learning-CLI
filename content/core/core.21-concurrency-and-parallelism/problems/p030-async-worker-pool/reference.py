import asyncio


async def process(items, worker, n_workers):
    """Process items with n_workers worker tasks.

    Return (results_in_input_order, errors) where errors is a list of
    (index, exception) sorted by index.
    """
    queue = asyncio.Queue()
    for index, item in enumerate(items):
        queue.put_nowait((index, item))
    results = [None] * len(items)
    errors = []

    async def run():
        while True:
            index, item = await queue.get()
            try:
                results[index] = await worker(item)
            except Exception as exc:
                errors.append((index, exc))
            finally:
                queue.task_done()

    tasks = [asyncio.create_task(run()) for _ in range(n_workers)]
    try:
        await queue.join()
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    errors.sort(key=lambda pair: pair[0])
    return results, errors
