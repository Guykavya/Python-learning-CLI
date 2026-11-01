from concurrent.futures import ThreadPoolExecutor, as_completed


def run_with_progress(funcs, workers, on_done):
    """Run funcs in a thread pool.

    Call on_done(index, result) in completion order, from the calling thread.
    Return the results in submission order.
    """
    results = [None] * len(funcs)
    if not funcs:
        return results
    with ThreadPoolExecutor(max_workers=workers) as pool:
        index_of = {pool.submit(f): i for i, f in enumerate(funcs)}
        for fut in as_completed(index_of):
            i = index_of[fut]
            results[i] = fut.result()
            on_done(i, results[i])
    return results
