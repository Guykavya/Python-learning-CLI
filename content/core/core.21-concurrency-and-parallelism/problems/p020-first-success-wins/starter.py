from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait


def first_success(funcs, timeout):
    """Return the value of the first function that succeeds.

    Raise RuntimeError if all fail, TimeoutError if none succeeds in time,
    ValueError if funcs is empty.
    """
    # TODO: this tries the functions one by one. It returns the first
    # success in LIST order (not time order) and ignores the timeout.
    last_error = None
    for f in funcs:
        try:
            return f()
        except Exception as err:
            last_error = err
    raise RuntimeError("all functions failed") from last_error
