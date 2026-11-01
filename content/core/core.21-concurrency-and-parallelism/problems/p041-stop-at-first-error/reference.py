from concurrent.futures import ThreadPoolExecutor, as_completed


def run_until_error(funcs, workers):
    """Run funcs on a pool; at the first failure cancel the queued ones.

    Return (results of the successful ones in input order, the error or None).
    """
    executor = ThreadPoolExecutor(max_workers=workers)
    futures = [executor.submit(func) for func in funcs]
    error = None
    try:
        for future in as_completed(futures):
            if future.exception() is not None:
                error = future.exception()
                break
    finally:
        # cancel everything still queued; wait for the ones already running
        executor.shutdown(wait=True, cancel_futures=True)
    results = [
        future.result()
        for future in futures
        if not future.cancelled() and future.exception() is None
    ]
    return results, error
