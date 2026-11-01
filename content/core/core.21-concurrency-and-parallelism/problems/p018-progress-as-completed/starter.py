from concurrent.futures import ThreadPoolExecutor, as_completed


def run_with_progress(funcs, workers, on_done):
    """Run funcs in a thread pool.

    Call on_done(index, result) in completion order, from the calling thread.
    Return the results in submission order.
    """
    # TODO: this runs the jobs one by one, so progress comes in input order
    # and nothing overlaps. Use a ThreadPoolExecutor and as_completed.
    results = []
    for i, f in enumerate(funcs):
        result = f()
        on_done(i, result)
        results.append(result)
    return results
