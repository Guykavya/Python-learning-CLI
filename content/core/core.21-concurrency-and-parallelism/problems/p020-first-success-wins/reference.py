import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait


def first_success(funcs, timeout):
    """Return the value of the first function that succeeds.

    Raise RuntimeError if all fail, TimeoutError if none succeeds in time,
    ValueError if funcs is empty.
    """
    if not funcs:
        raise ValueError("need at least one function")
    deadline = time.monotonic() + timeout
    pool = ThreadPoolExecutor(max_workers=len(funcs))
    pending = {pool.submit(f) for f in funcs}
    last_error = None
    try:
        while pending:
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError(f"no success within {timeout} s")
            done, pending = wait(pending, timeout=left, return_when=FIRST_COMPLETED)
            if not done:
                raise TimeoutError(f"no success within {timeout} s")
            for fut in done:
                err = fut.exception()
                if err is None:
                    return fut.result()
                last_error = err
        raise RuntimeError(f"all {len(funcs)} functions failed") from last_error
    finally:
        for fut in pending:
            fut.cancel()
        pool.shutdown(wait=False, cancel_futures=True)
