import pickle

import solution
from solution import chunk_ranges, parallel_sum_squares, sum_squares


def test_sum_squares():
    assert sum_squares(range(4)) == 14, "0 + 1 + 4 + 9 = 14."
    assert sum_squares(range(5, 7)) == 61, "25 + 36 = 61: the range does not start at 0 here."
    assert sum_squares(range(3, 3)) == 0, "An empty range sums to 0."


def test_worker_is_picklable():
    assert pickle.loads(pickle.dumps(sum_squares)) is sum_squares, (
        "sum_squares must be a top-level function so it can be pickled by name and sent to "
        "worker processes (not a lambda, not defined inside another function)."
    )


def test_chunks_exact():
    assert chunk_ranges(10, 3) == [range(0, 4), range(4, 7), range(7, 10)], (
        f"Got {chunk_ranges(10, 3)}. 10 = 4 + 3 + 3: sizes differ by at most 1, bigger first."
    )
    assert chunk_ranges(12, 4) == [range(0, 3), range(3, 6), range(6, 9), range(9, 12)], (
        "12 split into 4 is four chunks of 3."
    )
    assert chunk_ranges(7, 1) == [range(0, 7)], "One worker gets one chunk with everything."


def test_chunks_when_fewer_items_than_workers():
    assert chunk_ranges(2, 4) == [range(0, 1), range(1, 2)], (
        f"Got {chunk_ranges(2, 4)}. With n < k, make n chunks of size 1; never empty chunks."
    )
    assert chunk_ranges(0, 3) == [], "n == 0: no chunks at all."


def test_chunks_cover_everything_once():
    for n in (1, 5, 99, 100, 101):
        for k in (1, 2, 3, 7, 16):
            chunks = chunk_ranges(n, k)
            flat = [i for r in chunks for i in r]
            assert flat == list(range(n)), (
                f"chunk_ranges({n}, {k}) does not cover 0..{n - 1} exactly once, in order."
            )
            sizes = [len(r) for r in chunks]
            assert len(chunks) == min(n, k), f"chunk_ranges({n}, {k}) should give {min(n, k)} chunks."
            assert max(sizes) - min(sizes) <= 1, f"Sizes {sizes} differ by more than 1."
            assert sizes == sorted(sizes, reverse=True), f"Bigger chunks first, got sizes {sizes}."


def test_parallel_result_and_pool_usage(monkeypatch):
    created = []
    real = solution.ProcessPoolExecutor

    class SpyPool(real):
        def __init__(self, max_workers=None, *args, **kwargs):
            created.append(max_workers)
            super().__init__(max_workers, *args, **kwargs)

    monkeypatch.setattr(solution, "ProcessPoolExecutor", SpyPool)
    n = 200_000
    assert parallel_sum_squares(n, 4) == (n - 1) * n * (2 * n - 1) // 6, (
        "Wrong total. Each chunk's sum must be added exactly once."
    )
    assert len(created) == 1, (
        f"ProcessPoolExecutor was created {len(created)} times; create ONE pool and use it for "
        "all chunks (with ... as pool: pool.map(sum_squares, chunks))."
    )
    assert created[0] is not None and created[0] <= 4, (
        f"max_workers was {created[0]}. Pass max_workers so at most `workers` processes start."
    )


def test_small_n(monkeypatch):
    created = []
    real = solution.ProcessPoolExecutor

    class SpyPool(real):
        def __init__(self, max_workers=None, *args, **kwargs):
            created.append(max_workers)
            super().__init__(max_workers, *args, **kwargs)

    monkeypatch.setattr(solution, "ProcessPoolExecutor", SpyPool)
    assert parallel_sum_squares(3, 4) == 5, "n=3 with 4 workers: 0 + 1 + 4 = 5."
    assert created and created[0] <= 3, (
        f"max_workers was {created}. With only 3 chunks, starting 4 processes wastes one: "
        "use max_workers=len(chunks)."
    )
    assert parallel_sum_squares(0, 4) == 0, "n == 0 must return 0."
