from concurrent.futures import ProcessPoolExecutor


def sum_squares(r):
    """Sum of i * i for i in the range r. Runs inside a worker process."""
    raise NotImplementedError


def chunk_ranges(n, k):
    """Split range(n) into at most k near-equal consecutive ranges, bigger ones first."""
    return []


def parallel_sum_squares(n, workers):
    """sum(i * i for i in range(n)), computed by up to `workers` processes."""
    raise NotImplementedError


if __name__ == "__main__":
    print(parallel_sum_squares(1_000_000, 4))
