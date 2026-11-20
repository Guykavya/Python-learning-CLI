import random
from itertools import permutations

from solution import best_order, max_lateness


def model_lateness(jobs, order):
    t = 0
    worst = 0
    for i in order:
        t += jobs[i][0]
        worst = max(worst, t - jobs[i][1])
    return worst


def brute_best(jobs):
    return min(model_lateness(jobs, p) for p in permutations(range(len(jobs))))


def check_order(jobs, order):
    assert sorted(order) == list(range(len(jobs))), (
        f"best_order({jobs}) returned {order}: it must be a list of the indices 0..{len(jobs) - 1}, each once.")


def test_max_lateness_examples():
    jobs = [(5, 5), (1, 6)]
    assert max_lateness(jobs, [1, 0]) == 1, "Order [1, 0]: job 1 ends at 1, job 0 ends at 6 (deadline 5): lateness 1."
    assert max_lateness(jobs, [0, 1]) == 0, (
        "Order [0, 1]: the jobs end at 5 and 6, exactly on their deadlines. Lateness is max(0, finish - deadline), "
        "so the answer is 0, never negative.")


def test_max_lateness_uses_finish_time():
    assert max_lateness([(4, 3)], [0]) == 1, (
        "One job of length 4 with deadline 3 finishes at 4: lateness 1. Add the duration BEFORE comparing "
        "(the finish time counts, not the start time).")
    assert max_lateness([(2, 10), (3, 1)], [0, 1]) == 4, "The second job finishes at 5 with deadline 1: lateness 4."


def test_max_lateness_clamps_at_zero():
    assert max_lateness([(1, 100), (1, 100)], [0, 1]) == 0, "Everyone is early: the answer is 0, not a negative number."
    assert max_lateness([], []) == 0, "No jobs: maximum lateness 0."


def test_best_order_examples():
    jobs = [(5, 5), (1, 6)]
    order = best_order(jobs)
    check_order(jobs, order)
    assert max_lateness(jobs, order) == 0, (
        "Shortest job first runs the 1-unit job first and makes the 5-unit job late. Ignore durations: "
        "earliest DEADLINE first.")
    jobs = [(3, 6), (2, 8), (1, 9), (4, 9), (3, 14), (2, 15)]
    order = best_order(jobs)
    check_order(jobs, order)
    assert model_lateness(jobs, order) == 1, "The chapter's six jobs: the best maximum lateness is 1."


def test_least_slack_is_wrong():
    jobs = [(1, 2), (10, 10)]
    order = best_order(jobs)
    check_order(jobs, order)
    assert model_lateness(jobs, order) == 1, (
        "Least slack first (deadline - duration) runs the 10-unit job first and the short job ends 9 late. "
        "Earliest deadline first gives lateness 1.")


def test_empty_and_input_unchanged():
    assert list(best_order([])) == [], "No jobs: an empty order."
    jobs = [(2, 9), (1, 3), (4, 5)]
    copy = list(jobs)
    best_order(jobs)
    assert jobs == copy, "Do not sort the caller's list in place."


def test_random_against_permutations():
    rng = random.Random(20)
    for _ in range(300):
        n = rng.randint(1, 6)
        jobs = [(rng.randint(1, 6), rng.randint(0, 15)) for _ in range(n)]
        want = brute_best(jobs)
        got_l = max_lateness(jobs, list(range(n)))
        assert got_l == model_lateness(jobs, list(range(n))), (
            f"max_lateness({jobs}, {list(range(n))}) should be {model_lateness(jobs, list(range(n)))}, got {got_l}.")
        order = list(best_order(jobs))
        check_order(jobs, order)
        assert model_lateness(jobs, order) == want, (
            f"jobs={jobs}: your order {order} has maximum lateness {model_lateness(jobs, order)}, but the best "
            f"possible (all permutations tried) is {want}. Sort by deadline only.")


def test_larger_input():
    rng = random.Random(2020)
    jobs = [(rng.randint(1, 1000), rng.randint(0, 10**7)) for _ in range(10**4)]
    order = list(best_order(jobs))
    check_order(jobs, order)
    edf = sorted(range(len(jobs)), key=lambda i: jobs[i][1])
    assert model_lateness(jobs, order) == model_lateness(jobs, edf), "10,000 random jobs: not as good as EDF."
