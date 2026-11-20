import random

from solution import count_provinces


def matrix(n, roads):
    m = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for a, b in roads:
        m[a][b] = m[b][a] = 1
    return m


def brute(m):
    n = len(m)
    label = list(range(n))
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(n):
                if m[i][j] and label[i] != label[j]:
                    low = min(label[i], label[j])
                    label[i] = label[j] = low
                    changed = True
    return len(set(label))


def test_examples():
    assert count_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2, "Cities {0, 1} and {2}: 2 provinces."
    assert count_provinces([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) == 3, "No roads: every city is its own province."
    assert count_provinces([[1, 0, 1], [0, 1, 1], [1, 1, 1]]) == 1, (
        "0 and 1 are joined through 2: one province. Follow roads further than one step (a search or Union-Find).")


def test_count_components_not_roads():
    m = matrix(6, [(0, 1), (1, 2), (0, 2), (3, 4)])
    assert count_provinces(m) == 3, (
        "Provinces {0,1,2} (3 roads), {3,4} (1 road) and {5}: 3. Counting roads (or 1s) gives a different number.")
    m = matrix(4, [(2, 3)])
    assert count_provinces(m) == 3, "Only the road 2-3: provinces {0}, {1}, {2, 3}. Start a search from every unvisited city."


def test_single_city():
    assert count_provinces([[1]]) == 1, "One city is one province."


def test_random_against_brute_force():
    rng = random.Random(45)
    for _ in range(200):
        n = rng.randint(1, 15)
        roads = [tuple(rng.sample(range(n), 2)) for _ in range(rng.randint(0, n))] if n > 1 else []
        m = matrix(n, roads)
        expected = brute(m)
        assert count_provinces(m) == expected, f"n={n}, roads={roads}: expected {expected} provinces."


def test_chain_of_200_cities():
    n = 200
    m = matrix(n, [(i, i + 1) for i in range(n - 1)])
    assert count_provinces(m) == 1, "A chain of 200 cities is one province."
    m = matrix(n, [(i, i + 1) for i in range(0, n - 1, 2)])
    assert count_provinces(m) == 100, "100 separate pairs of cities: 100 provinces."
