import random

from solution import has_arbitrage


def best_cycle_product(n, rates):
    """Try every simple cycle (small n only) and return the largest product of rates."""
    best_rate = {}
    for a, b, r in rates:
        if r > best_rate.get((a, b), 0):
            best_rate[(a, b)] = r
    out = [[] for _ in range(n)]
    for (a, b), r in best_rate.items():
        out[a].append((b, r))
    best = 0.0

    def walk(start, u, prod, seen):
        nonlocal best
        for v, r in out[u]:
            if v == start:
                best = max(best, prod * r)
            elif v > start and v not in seen:
                seen.add(v)
                walk(start, v, prod * r, seen)
                seen.remove(v)

    for s in range(n):
        walk(s, s, 1.0, {s})
    return best


def consistent_market(rng, n, extra_edges):
    """Rates from hidden prices: every cycle multiplies to exactly 1 in exact arithmetic."""
    price = [rng.uniform(0.01, 100) for _ in range(n)]
    rates = []
    for _ in range(extra_edges):
        a, b = rng.randrange(n), rng.randrange(n)
        if a != b:
            rates.append((a, b, price[a] / price[b]))
    return rates


def test_the_examples():
    assert has_arbitrage(3, [(0, 1, 0.5), (1, 2, 4.0), (2, 0, 0.55)]) is True, "0.5 * 4.0 * 0.55 = 1.1 > 1: arbitrage."
    assert has_arbitrage(2, [(0, 1, 2.0), (1, 0, 0.5)]) is False, "2.0 * 0.5 = 1 exactly: no profit, so False."


def test_losing_cycles_are_not_arbitrage():
    got = has_arbitrage(3, [(0, 1, 0.5), (1, 2, 4.0), (2, 0, 0.45)])
    assert got is False, (
        f"0.5 * 4.0 * 0.45 = 0.9 < 1: this cycle loses money, expected False, got {got}. "
        "If you got True, check the sign: the weight is -log(r), not log(r).")


def test_the_cycle_need_not_touch_currency_zero():
    rates = [(0, 1, 1.0), (2, 3, 1.2), (3, 2, 0.9)]
    assert has_arbitrage(4, rates) is True, (
        "2 -> 3 -> 2 gives 1.2 * 0.9 = 1.08: arbitrage, even though currency 0 cannot reach it. "
        "Start every currency at distance 0, not only currency 0.")


def test_one_way_exchanges():
    assert has_arbitrage(2, [(0, 1, 3.0)]) is False, "a single exchange is not a cycle."
    assert has_arbitrage(2, [(0, 1, 3.0), (0, 1, 0.5)]) is False, "two exchanges 0 -> 1 and none back: no cycle at all."


def test_self_exchange():
    assert has_arbitrage(1, [(0, 0, 1.01)]) is True, "an exchange from a currency to itself at 1.01 is a 1 % profit."
    assert has_arbitrage(1, [(0, 0, 1.0)]) is False, "an exchange from a currency to itself at 1.0 is no profit."


def test_consistent_markets_need_a_tolerance():
    rng = random.Random(59)
    for trial in range(60):
        n = rng.randint(3, 12)
        rates = consistent_market(rng, n, 40)
        got = has_arbitrage(n, rates)
        assert got is False, (
            f"market {trial}: every rate comes from consistent prices, so every cycle gives back exactly 1, but you "
            "reported arbitrage. Float rounding makes some log-sums -2e-16: compare with a small tolerance "
            "(relax only if dist[a] + w < dist[b] - 1e-12).")


def test_a_small_real_profit_is_found():
    rng = random.Random(590)
    for trial in range(60):
        n = rng.randint(3, 12)
        rates = consistent_market(rng, n, 40)
        # one cycle through new exchanges, 0.2 % profit
        cyc = rng.sample(range(n), 3)
        price_ratio = [1.0, 1.0, 1.002]
        rates.append((cyc[0], cyc[1], price_ratio[0]))
        rates.append((cyc[1], cyc[2], price_ratio[1]))
        rates.append((cyc[2], cyc[0], price_ratio[2]))
        want = best_cycle_product(n, rates) > 1 + 1e-9 if n <= 8 else True
        got = has_arbitrage(n, rates)
        assert got is want, f"market {trial}: a cycle with a 0.2 % profit (or more) exists, expected {want}, got {got}."


def test_random_markets_against_all_cycles():
    rng = random.Random(591)
    checked = 0
    while checked < 300:
        n = rng.randint(1, 6)
        rates = [(rng.randrange(n), rng.randrange(n), rng.choice([0.5, 0.8, 0.9, 1.0, 1.1, 1.25, 2.0]))
                 for _ in range(rng.randint(0, 9))]
        best = best_cycle_product(n, rates)
        if 1 - 1e-6 < best < 1.001 and abs(best - 1) > 1e-9:
            continue                    # too close to 1 to be fair
        want = best > 1 + 1e-9
        got = has_arbitrage(n, rates)
        assert got is want, f"has_arbitrage({n}, {rates}): the best cycle multiplies by {best:.6f}, expected {want}, got {got}."
        checked += 1


def test_sixty_currencies():
    rng = random.Random(592)
    n = 60
    rates = consistent_market(rng, n, 2000)
    assert has_arbitrage(n, rates) is False, "a consistent market of 60 currencies and 2,000 exchanges has no arbitrage."
    a, b = rates[0][0], rates[0][1]
    rates.append((b, a, (1 / rates[0][2]) * 1.01))
    assert has_arbitrage(n, rates) is True, "adding one exchange back at a 1 % better rate creates arbitrage."
