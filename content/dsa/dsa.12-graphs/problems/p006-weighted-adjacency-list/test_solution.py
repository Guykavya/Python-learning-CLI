import random

from solution import weighted_adj


def model(n, edges, directed):
    best = {}
    for u, v, w in edges:
        pairs = [(u, v)] if directed else [(u, v), (v, u)]
        for a, b in pairs:
            if (a, b) not in best or w < best[(a, b)]:
                best[(a, b)] = w
    adj = [{} for _ in range(n)]
    for (a, b), w in best.items():
        adj[a][b] = w
    return adj


def test_the_examples():
    got = weighted_adj(3, [(0, 1, 4), (1, 2, 1), (1, 0, 3)])
    assert got == [{1: 3}, {0: 3, 2: 1}, {1: 1}], (
        f"(0, 1, 4) and (1, 0, 3) are the same undirected pair: both adj[0][1] and adj[1][0] keep the smaller weight 3. Got {got}.")
    got = weighted_adj(2, [(0, 1, 7), (0, 1, 9)], directed=True)
    assert got == [{1: 7}, {}], f"Directed parallel edges 7 and 9: keep 7 (the smaller), and vertex 1 has no outgoing edges. Got {got}."


def test_last_weight_does_not_win():
    got = weighted_adj(2, [(0, 1, 2), (0, 1, 5)])
    assert got[0][1] == 2 and got[1][0] == 2, f"The second edge is longer: keep 2, not the last weight 5. Got {got}."


def test_zero_and_negative_weights():
    got = weighted_adj(2, [(0, 1, 0), (0, 1, 4)])
    assert got[0][1] == 0, "A weight of 0 is a real edge and the smallest: do not test it with `if adj[u].get(v)` (0 is falsy)."
    got = weighted_adj(2, [(0, 1, -3), (1, 0, 2)], directed=True)
    assert got == [{1: -3}, {0: 2}], "Directed: (0, 1) and (1, 0) are different edges."


def test_isolated_and_self_loop():
    got = weighted_adj(3, [(1, 1, 5), (1, 1, 2)])
    assert got == [{}, {1: 2}, {}], f"A self loop keeps its smallest weight; vertices 0 and 2 get empty dicts. Got {got}."
    got = weighted_adj(3, [])
    assert got == [{}, {}, {}], "No edges: n empty dictionaries."
    got[0][2] = 1
    assert got[1] == {}, "Your dictionaries are shared: use [{} for _ in range(n)], not [{}] * n."


def test_random_against_a_model():
    rng = random.Random(1206)
    for _ in range(400):
        n = rng.randint(1, 6)
        edges = [(rng.randrange(n), rng.randrange(n), rng.randint(-3, 9)) for _ in range(rng.randint(0, 15))]
        for directed in (False, True):
            want = model(n, edges, directed)
            got = weighted_adj(n, edges, directed)
            assert got == want, f"weighted_adj({n}, {edges}, directed={directed}) should be {want}, got {got}."
