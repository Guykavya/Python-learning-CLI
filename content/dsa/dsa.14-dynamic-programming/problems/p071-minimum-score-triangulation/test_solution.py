import pathlib
import random
import subprocess
import sys

from solution import min_score_triangulation

HERE = pathlib.Path(__file__).parent


def brute(values):
    """Every triangulation, by clipping ears: remove a corner together with its two neighbours' triangle."""
    if len(values) == 3:
        return values[0] * values[1] * values[2]
    best = None
    for v in range(len(values)):
        tri = values[v - 1] * values[v] * values[(v + 1) % len(values)]
        rest = values[:v] + values[v + 1:]
        score = tri + brute(rest)
        if best is None or score < best:
            best = score
    return best


def test_examples():
    assert min_score_triangulation([1, 2, 3]) == 6, "A triangle is already triangulated: 1*2*3 = 6."
    assert min_score_triangulation([3, 7, 4, 5]) == 144, (
        "Expected 144 (cut 0-2: 84 + 60). The other cut gives 245; take the min over the third corner k.")
    assert min_score_triangulation([1, 3, 1, 4, 1, 5]) == 13, "Expected 13."


def test_both_parts_keep_k():
    assert min_score_triangulation([1, 2, 3, 4]) == 18, (
        "Expected 18 (cut 0-2: 1*2*3 + 1*3*4). If you got 8, the triangle (i, k, j) shares corner k with both parts: f(i, k) + f(k, j), not "
        "f(i, k) + f(k+1, j) as in matrix chain.")


def test_random_against_all_triangulations():
    rng = random.Random(71)
    for _ in range(300):
        values = [rng.randint(1, 9) for _ in range(rng.randint(3, 7))]
        want = brute(values)
        got = min_score_triangulation(list(values))
        assert got == want, (
            f"values={values}: expected {want} (every triangulation tried), got {got}. "
            "f(i, j) = min over i < k < j of f(i, k) + f(k, j) + v[i]*v[k]*v[j]; f(i, i+1) = 0; short pieces first.")


def test_large_input_in_time():
    rng = random.Random(7100)
    values = [rng.randint(1, 100) for _ in range(150)]
    code = (
        "import sys\n"
        "from solution import min_score_triangulation\n"
        "values = [int(x) for x in sys.stdin.read().split()]\n"
        "print(min_score_triangulation(values), min_score_triangulation([1] * 150))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, input=" ".join(map(str, values)),
                           capture_output=True, text=True, timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 150 corners. A recursion over the third corner without a memo is exponential: "
        "add a memo on (i, j), or fill the table by gap.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["389547", "148"], (
        f"Expected 389547 for the random polygon and 148 for 150 ones (148 triangles of score 1); "
        f"got {r.stdout.split()}.")
