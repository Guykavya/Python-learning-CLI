from concurrent.futures import ProcessPoolExecutor


def sum_squares(r):
    """Sum of i * i for i in the range r. Runs inside a worker process."""
    return sum(i * i for i in r)


def chunk_ranges(n, k):
    """Split range(n) into at most k near-equal consecutive ranges, bigger ones first."""
    k = min(k, n)
    if k <= 0:
        return []
    size, extra = divmod(n, k)
    chunks = []
    start = 0
    for i in range(k):
        stop = start + size + (1 if i < extra else 0)
        chunks.append(range(start, stop))
        start = stop
    return chunks


def parallel_sum_squares(n, workers):
    """sum(i * i for i in range(n)), computed by up to `workers` processes."""
    chunks = chunk_ranges(n, workers)
    if not chunks:
        return 0
    with ProcessPoolExecutor(max_workers=len(chunks)) as pool:
        return sum(pool.map(sum_squares, chunks))


if __name__ == "__main__":
    print(parallel_sum_squares(1_000_000, 4))
