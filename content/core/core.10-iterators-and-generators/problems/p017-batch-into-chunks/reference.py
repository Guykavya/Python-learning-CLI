from itertools import islice


def batches(iterable, n):
    if n < 1:
        raise ValueError("n must be at least 1")
    it = iter(iterable)
    while True:
        chunk = list(islice(it, n))
        if not chunk:
            return
        yield chunk
