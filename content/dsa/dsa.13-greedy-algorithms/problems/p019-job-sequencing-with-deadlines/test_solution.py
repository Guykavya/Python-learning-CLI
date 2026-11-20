import random

from solution import max_profit


def brute(jobs):
    """Try every subset; a subset is possible if, sorted by deadline, the k-th job (0-based) fits in slot k+1."""
    best = 0
    for mask in range(1 << len(jobs)):
        chosen = sorted((jobs[i] for i in range(len(jobs)) if mask >> i & 1), key=lambda j: j[0])
        if all(k + 1 <= j[0] for k, j in enumerate(chosen)):
            best = max(best, sum(j[1] for j in chosen))
    return best


def test_chapter_example():
    jobs = [(2, 100), (1, 19), (2, 27), (1, 25), (3, 15)]
    assert max_profit(jobs) == 142, (
        "Expected 142 (27 in slot 1, 100 in slot 2, 15 in slot 3). Take jobs by profit, highest first, "
        "and put each in the LATEST free slot at or before its deadline.")


def test_empty_and_single():
    assert max_profit([]) == 0, "No jobs: profit 0 (careful: max() of an empty list crashes)."
    assert max_profit([(1, 7)]) == 7, "One job with deadline 1 runs in slot 1."


def test_all_need_slot_one():
    assert max_profit([(1, 5), (1, 9), (1, 3)]) == 9, (
        "All three jobs have deadline 1, so only one can run: take the most profitable, 9.")


def test_latest_slot_matters():
    assert max_profit([(3, 8), (1, 7)]) == 15, (
        "(3, 8) is taken first. If it grabs slot 1 (the EARLIEST free slot), (1, 7) has nowhere to go. "
        "Put each job in the LATEST free slot before its deadline: 8 in slot 3, 7 in slot 1.")
    assert max_profit([(3, 8), (1, 7), (1, 6)]) == 15, (
        "Expected 15. Counting 'jobs taken so far < deadline' is not the same as having a free slot.")


def test_deadline_order_alone_is_wrong():
    assert max_profit([(1, 1), (2, 50), (2, 60)]) == 110, (
        "Expected 110 (50 and 60 in slots 1 and 2). Taking jobs by earliest deadline keeps the cheap job 1 "
        "and loses one of the expensive ones.")


def test_huge_deadlines():
    assert max_profit([(10**6, 5), (1, 3), (10**6, 4)]) == 12, (
        "Expected 12: all three jobs fit (slots 1, 2 and 3). Deadlines can be far beyond the number of jobs. "
        "With n jobs, no job needs a slot later than n: cap the deadline at n instead of building a list of "
        "max(deadline) slots (the statement allows deadlines up to 10**9).")


def test_input_not_changed():
    jobs = [(2, 1), (1, 9), (2, 5)]
    copy = list(jobs)
    max_profit(jobs)
    assert jobs == copy, "Do not sort the caller's list in place; use sorted(...)."


def test_random_against_brute_force():
    rng = random.Random(19)
    for _ in range(400):
        n = rng.randint(1, 8)
        jobs = [(rng.randint(1, 5), rng.randint(1, 30)) for _ in range(n)]
        want = brute(list(jobs))
        got = max_profit(list(jobs))
        assert got == want, (
            f"jobs={jobs}: expected {want}, got {got} (checked by trying every subset). Use profit order "
            "with the latest free slot, or deadline order with a min-heap that drops the cheapest job.")


def test_larger_input():
    rng = random.Random(1919)
    jobs = [(rng.randint(1, 2000), rng.randint(1, 10**6)) for _ in range(2000)]
    import heapq
    heap = []
    for d, p in sorted(jobs):
        heapq.heappush(heap, p)
        if len(heap) > d:
            heapq.heappop(heap)
    assert max_profit(jobs) == sum(heap), "2000 random jobs: your total differs from the heap method's total."
