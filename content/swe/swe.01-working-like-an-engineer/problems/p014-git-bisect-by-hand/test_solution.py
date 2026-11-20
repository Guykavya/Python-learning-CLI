import math

from solution import first_bad


def run(n, k):
    commits = list(range(n))        # commits[i] is bad when i >= k (k >= 1)
    calls = []

    def is_bad(c):
        calls.append(c)
        return c >= k

    return first_bad(commits, is_bad), calls


def test_example():
    commits = ["c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7"]
    assert first_bad(commits, lambda c: c in {"c5", "c6", "c7"}) == "c5"


def test_two_commits_need_no_test():
    got, calls = run(2, 1)
    assert got == 1 and calls == [], "With one good and one bad commit there is nothing to test: the bad one is the answer."


def test_three_commits():
    assert run(3, 1)[0] == 1
    assert run(3, 2)[0] == 2


def test_every_position_in_a_history_of_1000():
    n = 1000
    limit = math.ceil(math.log2(n)) + 1
    for k in list(range(1, 40)) + [499, 500, 501, 998, 999]:
        got, calls = run(n, k)
        assert got == k, f"The first bad commit is {k}, got {got}."
        assert len(calls) <= limit, (
            f"{len(calls)} tests for {n} commits (limit {limit}): that is a linear search. Halve the range each time.")


def test_endpoints_are_never_tested():
    got, calls = run(50, 20)
    assert 0 not in calls and 49 not in calls, "commits[0] is known good and commits[-1] is known bad: do not test them."
