from solution import counterexample

COINS = (4, 3, 1)


def greedy_coins(amount, coins=COINS):
    used = []
    for c in coins:
        while amount >= c:
            amount -= c
            used.append(c)
    return used


def fewest_table(limit):
    best = [0] + [None] * limit
    for a in range(1, limit + 1):
        best[a] = min(best[a - c] + 1 for c in COINS if c <= a)
    return best


def get():
    result = counterexample()
    assert isinstance(result, tuple) and len(result) == 3, (
        "Return a tuple (amount, machine, better), for example `return (amount, [..], [..])`.")
    return result


def test_amount_is_valid():
    amount, _, _ = get()
    assert isinstance(amount, int), f"The amount must be an int, got {amount!r}."
    assert 1 <= amount <= 1000, f"The amount must be between 1 and 1000, got {amount}."
    assert amount != 6, "6 is the chapter's example. Find another amount (try the ones just above 6)."


def test_machine_list_is_what_greedy_pays():
    amount, machine, _ = get()
    expected = greedy_coins(amount)
    assert list(machine) == expected, (
        f"For {amount} the machine pays {expected}, not {machine}. Trace the code: as many 4s as fit, then 3s, "
        "then 1s.")


def test_better_is_valid_and_fewest():
    amount, _, better = get()
    better = list(better)
    assert all(c in (1, 3, 4) for c in better), f"better={better} may only use coins 1, 3 and 4."
    assert sum(better) == amount, f"better={better} adds up to {sum(better)}, not {amount}."
    best = fewest_table(amount)[amount]
    assert len(better) == best, (
        f"better={better} uses {len(better)} coins, but {amount} can be paid with {best}. Give the FEWEST.")


def test_machine_really_loses():
    amount, _, _ = get()
    machine = greedy_coins(amount)
    best = fewest_table(amount)[amount]
    assert len(machine) > best, (
        f"For {amount} the machine pays {machine} ({len(machine)} coins), which is already the fewest. "
        "Greedy wins on this amount; look for one where a 4 leaves a remainder that needs 1s.")
