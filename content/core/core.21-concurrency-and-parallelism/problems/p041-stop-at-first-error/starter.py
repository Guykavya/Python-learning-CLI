from concurrent.futures import ThreadPoolExecutor, as_completed


def run_until_error(funcs, workers):
    """Run funcs on a pool; at the first failure cancel the queued ones.

    Return (results of the successful ones in input order, the error or None).
    """
    raise NotImplementedError("submit all, watch as_completed, cancel the rest on an error")
