import asyncio


async def process(items, worker, n_workers):
    """Process items with n_workers worker tasks.

    Return (results_in_input_order, errors) where errors is a list of
    (index, exception) sorted by index.
    """
    # TODO: this does one item at a time and ignores n_workers.
    results = []
    errors = []
    for i, item in enumerate(items):
        try:
            results.append(await worker(item))
        except Exception as exc:
            results.append(None)
            errors.append((i, exc))
    return results, errors
