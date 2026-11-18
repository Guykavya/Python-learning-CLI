import pathlib
import random
import subprocess
import sys

from solution import can_complete_circuit

HERE = pathlib.Path(__file__).parent


def valid_starts(gas, cost):
    """Drive round from every start (slow but obviously right)."""
    n = len(gas)
    good = []
    for s in range(n):
        tank = 0
        for k in range(n):
            i = (s + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                break
        else:
            good.append(s)
    return good


def test_chapter_examples():
    assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3, (
        "Expected 3. The net gains are [-2, -2, -2, 3, 3]: the tank goes negative at 0, 1 and 2, so restart "
        "after each; from 3 the tank never drops below 0.")
    assert can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1, (
        "Expected -1: sum(gas) = 9 < sum(cost) = 10, so no start can work. Check the totals first.")
    assert can_complete_circuit([5], [4]) == 0, "One station with enough gas: start at 0."


def test_one_station_not_enough():
    assert can_complete_circuit([3], [4]) == -1, "One station, 3 litres, cost 4: impossible."


def test_restart_after_the_failing_station():
    assert can_complete_circuit([0, 0, 5], [1, 1, 3]) == 2, (
        "Expected 2. Station 0 fails at once, then station 1 fails: the next candidate is i + 1, not i.")
    assert can_complete_circuit([0, 3, 0, 2], [3, 1, 1, 0]) == 1, (
        "Expected 1 (net gains [-3, 2, -1, 2]). When you restart, empty the tank: the new start begins with "
        "0 litres, not with the old debt of -3.")


def test_random_against_brute_force():
    rng = random.Random(24)
    tested = 0
    while tested < 800:
        n = rng.randint(1, 7)
        gas = [rng.randint(0, 6) for _ in range(n)]
        cost = [rng.randint(0, 6) for _ in range(n)]
        good = valid_starts(gas, cost)
        if len(good) > 1:
            continue                      # the problem promises at most one valid start
        tested += 1
        want = good[0] if good else -1
        got = can_complete_circuit(list(gas), list(cost))
        assert got == want, (
            f"gas={gas}, cost={cost}: expected {want} (every start tried), got {got}. Return -1 when "
            "sum(gas) < sum(cost); otherwise restart at i + 1 with an empty tank whenever it goes negative.")


def test_large_input_is_linear():
    code = (
        "from solution import can_complete_circuit\n"
        "n = 10**5\n"
        "gas = [1] * n\n"
        "cost = [1] * n\n"
        "cost[n // 2 - 1] = 2\n"
        "gas[n // 2] = 2\n"
        "print(can_complete_circuit(gas, cost))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100,000 stations. Driving round from every start is O(n^2); one pass is enough.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["50000"], f"Large input: expected start 50000, got {r.stdout.split()}."
