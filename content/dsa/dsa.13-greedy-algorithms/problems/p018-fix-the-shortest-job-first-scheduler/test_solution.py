import random
from itertools import permutations

from solution import schedule


def total_waiting(durations):
    wait = elapsed = 0
    for d in durations:
        wait += elapsed
        elapsed += d
    return wait


def test_complaint_example():
    order, wait = schedule([("lint", 6), ("test", 8), ("docs", 7), ("fmt", 3)])
    assert order == ["fmt", "lint", "docs", "test"], "The order was already right: shortest duration first."
    assert wait != 24, (
        "24 is the time the LAST job finishes: `total_wait = elapsed` overwrites the total each time instead of "
        "adding to it.")
    assert wait != 52, (
        "52 is the sum of FINISH times (3 + 9 + 16 + 24). You now add to the total, but after adding the job's own "
        "duration. A job waits only for the jobs before it: add `elapsed` first, then the duration.")
    assert wait == 28, f"Waits are 0, 3, 9, 16, total 28; you returned {wait}."


def test_two_jobs():
    assert schedule([("b", 5), ("a", 2)]) == (["a", "b"], 2), (
        "Job a (2 min) runs first and waits 0; job b waits 2. Total 2.")


def test_edge_cases():
    assert schedule([]) == ([], 0), "No jobs: ([], 0)."
    assert schedule([("only", 9)]) == (["only"], 0), "A single job starts at once: it waits 0, not 9."


def test_ties_keep_input_order():
    order, wait = schedule([("x", 4), ("y", 1), ("z", 4), ("w", 1)])
    assert order == ["y", "w", "x", "z"], (
        "Equal durations keep their input order (y before w, x before z). Sort by duration only; `sorted` is stable.")
    assert wait == 0 + 1 + 2 + 6, f"Waits 0, 1, 2, 6: total 9; got {wait}."


def test_input_not_changed():
    jobs = [("lint", 6), ("fmt", 3)]
    schedule(jobs)
    assert jobs == [("lint", 6), ("fmt", 3)], "Do not sort the caller's list in place."


def test_random_against_all_orders():
    rng = random.Random(18)
    for _ in range(300):
        n = rng.randint(0, 6)
        jobs = [(f"j{i}", rng.randint(0, 15)) for i in range(n)]
        order, wait = schedule(list(jobs))
        durations = dict(jobs)
        assert sorted(order) == sorted(name for name, _ in jobs), f"jobs={jobs}: every job must appear once in the order."
        assert wait == total_waiting([durations[name] for name in order]), (
            f"jobs={jobs}: your order {order} has total waiting {total_waiting([durations[n] for n in order])}, "
            f"but you returned {wait}. Add `elapsed` to the total BEFORE adding the job's duration.")
        best = min((total_waiting(p) for p in permutations([d for _, d in jobs])), default=0)
        assert wait == best, f"jobs={jobs}: the smallest total waiting time is {best}, you returned {wait}."
