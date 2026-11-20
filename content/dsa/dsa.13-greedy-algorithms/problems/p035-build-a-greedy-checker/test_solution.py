import random

from solution import first_counterexample, stress_test

# ---------- three problems from this module, each with a greedy and an obviously right brute force

# 1. Coin change with coins 1, 3, 4 (section 9): greedy is WRONG.
def greedy_coins(amount):
    count = 0
    for c in (4, 3, 1):
        count += amount // c
        amount %= c
    return count


def dp_coins(amount):
    best = [0] + [None] * amount
    for a in range(1, amount + 1):
        best[a] = 1 + min(best[a - c] for c in (1, 3, 4) if c <= a)
    return best[amount]


# 2. Activity selection by earliest finish (section 4): greedy is CORRECT. Touching intervals do not overlap.
def earliest_finish(events):
    events.sort(key=lambda ev: ev[1])          # sorts in place on purpose: the checker must copy
    count, last_end = 0, None
    for s, e in events:
        if last_end is None or s >= last_end:
            count += 1
            last_end = e
    return count


def brute_activities(events):
    best = 0
    for mask in range(1 << len(events)):
        chosen = sorted(events[i] for i in range(len(events)) if mask >> i & 1)
        if all(chosen[k][1] <= chosen[k + 1][0] for k in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return best


def random_events(rng):
    out = []
    for _ in range(rng.randint(0, 6)):
        s = rng.randint(0, 10)
        out.append((s, s + rng.randint(1, 6)))
    return out


# 3. 0/1 knapsack, capacity 10, highest value first (section 8): greedy is WRONG. Items are (value, weight).
CAPACITY = 10


def value_first(items):
    items.sort(key=lambda it: -it[0])          # sorts in place on purpose
    room, total = CAPACITY, 0
    for value, weight in items:
        if weight <= room:
            room -= weight
            total += value
    return total


def brute_knapsack(items):
    best = 0
    for mask in range(1 << len(items)):
        chosen = [items[i] for i in range(len(items)) if mask >> i & 1]
        if sum(w for _, w in chosen) <= CAPACITY:
            best = max(best, sum(v for v, _ in chosen))
    return best


def random_items(rng):
    return [(rng.randint(1, 10), rng.randint(1, 8)) for _ in range(rng.randint(1, 5))]


def expected_stress(greedy, brute, make_input, trials, seed):
    """What a correct stress_test must return: one Random(seed), make_input once per trial, copies for each call."""
    rng = random.Random(seed)
    for _ in range(trials):
        inst = make_input(rng)
        g = greedy(list(inst) if isinstance(inst, list) else inst)
        b = brute(list(inst) if isinstance(inst, list) else inst)
        if g != b:
            return (inst, g, b)
    return None


# ---------- first_counterexample

def test_coins_first_counterexample():
    got = first_counterexample(greedy_coins, dp_coins, range(20))
    assert got == 6, (
        f"Coins 1, 3, 4: the first amount where greedy differs from DP is 6 (4+1+1 versus 3+3); got {got!r}. "
        "Go through the instances in order and return the FIRST difference.")


def test_none_when_all_agree():
    assert first_counterexample(greedy_coins, dp_coins, [0, 1, 2, 3, 4, 5]) is None, (
        "Amounts 0..5: greedy and DP agree on all of them, so return None.")
    assert first_counterexample(greedy_coins, dp_coins, []) is None, "No instances: return None."


def test_zero_is_a_real_instance():
    always_wrong = lambda x: -1
    got = first_counterexample(always_wrong, dp_coins, [0, 5])
    assert got == 0, (
        f"The very first instance, 0, already differs (greedy -1, brute 0), so return 0; got {got!r}. "
        "Do not treat 0 as 'nothing found'.")


def test_stops_at_the_first_difference():
    seen = []

    def greedy(x):
        seen.append(x)
        if x == "STOP":
            raise AssertionError("first_counterexample kept going after the first difference: return at once.")
        return greedy_coins(x)

    def brute(x):
        if x == "STOP":
            raise AssertionError("first_counterexample kept going after the first difference: return at once.")
        return dp_coins(x)

    assert first_counterexample(greedy, brute, [5, 6, 7, "STOP"]) == 6, "6 is the first counterexample."
    assert "STOP" not in seen, "Do not call the functions on instances after the first counterexample."


def test_works_with_any_iterable():
    got = first_counterexample(greedy_coins, dp_coins, (a for a in range(4, 12)))
    assert got == 6, f"instances may be a generator, not only a list; expected 6, got {got!r}."


def test_activity_selection_is_correct():
    rng = random.Random(35)
    instances = [random_events(rng) for _ in range(300)]
    got = first_counterexample(earliest_finish, brute_activities, instances)
    assert got is None, (
        f"Earliest finish is a correct greedy, but your checker reported {got!r}. Compare greedy(instance) with "
        "brute(instance) on the SAME input: give each function its own copy (the greedy sorts in place).")


def test_knapsack_counterexample_is_reported_unchanged():
    instances = [[(5, 5), (5, 5)], [(7, 5), (10, 6), (7, 5)], [(1, 1)]]
    originals = [list(x) for x in instances]
    got = first_counterexample(value_first, brute_knapsack, instances)
    assert got == originals[1], (
        f"Expected the ORIGINAL second instance {originals[1]} (value first takes 10, the best is 7 + 7 = 14); "
        f"got {got!r}. If it looks sorted, the greedy sorted the caller's list: pass list(instance) to each call.")
    assert instances == originals, "The instances must not be changed: give each function a copy of a list instance."


# ---------- stress_test

def test_stress_finds_the_coin_counterexample():
    make = lambda rng: rng.randint(0, 30)
    got = stress_test(greedy_coins, dp_coins, make, trials=500, seed=1)
    want = expected_stress(greedy_coins, dp_coins, make, 500, 1)
    assert got == want, (
        f"stress_test(..., trials=500, seed=1) should return {want}, got {got!r}. Create ONE random.Random(seed) "
        "before the loop, call make_input(rng) once per trial, and return (instance, greedy answer, brute answer).")
    instance, g, b = got
    assert g == greedy_coins(instance) and b == dp_coins(instance) and g != b, "The tuple must hold the two answers."


def test_stress_is_reproducible():
    make = lambda rng: rng.randint(0, 40)
    a = stress_test(greedy_coins, dp_coins, make, trials=200, seed=7)
    b = stress_test(greedy_coins, dp_coins, make, trials=200, seed=7)
    assert a == b, "Two runs with the same seed must find the same counterexample. Use random.Random(seed)."


def test_stress_uses_one_generator():
    made = []

    def make(rng):
        x = rng.randint(0, 10**9)
        made.append(x)
        return x

    same = lambda x: 0
    assert stress_test(same, same, make, trials=50, seed=3) is None, "Greedy and brute always agree: None."
    assert len(made) == 50, f"make_input must be called exactly once per trial: 50 trials, {len(made)} calls."
    assert len(set(made)) > 1, (
        "Every trial produced the same instance: create random.Random(seed) ONCE, before the loop, not per trial.")
    rng = random.Random(3)
    assert made == [rng.randint(0, 10**9) for _ in range(50)], (
        "The instances must come from random.Random(seed), passed to make_input, and nothing else may use it.")


def test_stress_stops_early():
    calls = []

    def make(rng):
        calls.append(1)
        return len(calls)

    wrong_from_3 = lambda x: x if x < 3 else -x
    got = stress_test(wrong_from_3, lambda x: x, make, trials=100, seed=0)
    assert got == (3, -3, 3), f"The third instance (3) is the first difference: expected (3, -3, 3), got {got!r}."
    assert len(calls) == 3, f"Stop at the first difference: make_input was called {len(calls)} times, expected 3."


def test_stress_activity_selection_finds_nothing():
    got = stress_test(earliest_finish, brute_activities, random_events, trials=400, seed=0)
    assert got is None, (
        f"Earliest finish is correct, but stress_test reported {got!r}. Each function needs its own copy of the "
        "instance (the greedy sorts in place).")


def test_stress_knapsack_reports_original_instance():
    got = stress_test(value_first, brute_knapsack, random_items, trials=500, seed=5)
    want = expected_stress(value_first, brute_knapsack, random_items, 500, 5)
    assert want is not None, "(test self-check) value-first knapsack should fail somewhere in 500 trials."
    assert got == want, (
        f"Expected {want}, got {got!r}. Report the instance exactly as make_input produced it (not sorted by the "
        "greedy), with the greedy's and the brute force's answers.")


def test_default_arguments():
    make = lambda rng: rng.randint(0, 30)
    got = stress_test(greedy_coins, dp_coins, make)
    want = expected_stress(greedy_coins, dp_coins, make, 1000, 0)
    assert got == want, f"Defaults are trials=1000, seed=0: expected {want}, got {got!r}."
