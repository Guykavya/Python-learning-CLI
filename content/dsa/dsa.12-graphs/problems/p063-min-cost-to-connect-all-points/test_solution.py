import random
import time

from solution import min_cost_connect_points


def kruskal_points(points):
    n = len(points)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1]), i, j))
    edges.sort()
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    for w, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj
            total += w
    return total


def test_the_examples():
    got = min_cost_connect_points([(0, 0), (2, 2), (3, 10), (5, 2), (7, 0)])
    assert got == 20, f"expected 20, got {got}. The cost of a join is |dx| + |dy| (Manhattan), not the straight-line length."
    assert min_cost_connect_points([(3, 12), (-2, 5), (-4, 1)]) == 18, "three points: 12 + 6 = 18."
    assert min_cost_connect_points([(0, 0)]) == 0, "one point: nothing to join, 0."


def test_returns_an_int():
    got = min_cost_connect_points([(0, 0), (1, 1)])
    assert got == 2 and isinstance(got, int), f"(0,0) and (1,1) cost |1| + |1| = 2 as an int; got {got!r}."


def test_nearest_to_any_tree_point_not_to_the_last():
    pts = [(0, 0), (5, 0), (-6, 0)]
    got = min_cost_connect_points(pts)
    assert got == kruskal_points(pts) == 11, (
        f"expected 11: (0,0)-(5,0) costs 5 and (0,0)-(-6,0) costs 6; got {got}. If you got 16, you joined (-6,0) to "
        "the LAST point added, (5,0). Join the point that is nearest to ANY point of the tree.")


def test_two_points_far_apart_and_negative_coordinates():
    assert min_cost_connect_points([(-10 ** 6, -10 ** 6), (10 ** 6, 10 ** 6)]) == 4 * 10 ** 6, "|2e6| + |2e6| = 4e6."


def test_random_against_kruskal():
    rng = random.Random(63)
    for _ in range(150):
        n = rng.randint(1, 40)
        pts = list({(rng.randint(-50, 50), rng.randint(-50, 50)) for _ in range(n)})
        want = kruskal_points(pts)
        got = min_cost_connect_points(pts)
        assert got == want, f"min_cost_connect_points({pts}): expected {want}, got {got}."


def test_thousand_points():
    rng = random.Random(630)
    pts = list({(rng.randint(-10 ** 6, 10 ** 6), rng.randint(-10 ** 6, 10 ** 6)) for _ in range(1000)})
    want = kruskal_points(pts)
    start = time.perf_counter()
    got = min_cost_connect_points(pts)
    took = time.perf_counter() - start
    assert got == want, f"1,000 points: expected {want}, got {got}."
    assert took < 30, f"1,000 points took {took:.1f} s; Prim with an array is O(n^2), about a million steps."
