import pathlib
import random
import subprocess
import sys

from solution import matrix_chain_cost

HERE = pathlib.Path(__file__).parent


def brute(dims, i=0, j=None):
    """Try every bracketing: plain recursion over the last split. Exponential; tiny inputs only."""
    if j is None:
        j = len(dims) - 2
    if i == j:
        return 0
    return min(brute(dims, i, k) + brute(dims, k + 1, j) + dims[i] * dims[k + 1] * dims[j + 1]
               for k in range(i, j))


def test_examples():
    assert matrix_chain_cost([10, 30, 5, 60]) == 4500, "Expected 4500: (A0 A1) A2 = 10*30*5 + 10*5*60."
    assert matrix_chain_cost([40, 20, 30, 10, 30]) == 26000, (
        "Expected 26000. If your answer is too small, f[k+1][j] was read before it was filled: loop by length.")
    assert matrix_chain_cost([5, 10, 3, 12, 5]) == 405, "Expected 405: (A0 A1)(A2 A3) = 150 + 180 + 75."


def test_one_and_two_matrices():
    assert matrix_chain_cost([7, 3]) == 0, "One matrix: no multiplication, cost 0."
    assert matrix_chain_cost([2, 3, 4]) == 24, "Two matrices: one way, 2*3*4 = 24."


def test_greedy_is_not_enough():
    assert matrix_chain_cost([8, 9, 4, 6, 4, 4]) == 576, (
        "Expected 576. 'Cheapest adjacent multiplication first' gives 592: try every split point k.")


def test_random_against_brute():
    rng = random.Random(69)
    for _ in range(300):
        dims = [rng.randint(1, 20) for _ in range(rng.randint(2, 8))]
        want = brute(dims)
        got = matrix_chain_cost(list(dims))
        assert got == want, (
            f"dims={dims}: expected {want} (every bracketing tried), got {got}. The last step costs "
            "dims[i] * dims[k+1] * dims[j+1], and both parts must be filled before f[i][j].")


def test_large_input_in_time():
    rng = random.Random(6900)
    dims = [rng.randint(1, 100) for _ in range(151)]
    code = (
        "import sys\n"
        "from solution import matrix_chain_cost\n"
        "dims = [int(x) for x in sys.stdin.read().split()]\n"
        "print(matrix_chain_cost(dims), matrix_chain_cost(list(range(1, 152))))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, input=" ".join(map(str, dims)),
                           capture_output=True, text=True, timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 150 matrices. Trying every bracketing is exponential: add a memo on (i, j), "
        "or fill the table by length (O(n^3)).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    # dims 1, 2, ..., 151: multiplying left to right is optimal, cost sum of 1 * (m+1) * (m+2) for m = 1..149
    want_increasing = sum((m + 1) * (m + 2) for m in range(1, 150))
    assert r.stdout.split() == ["338204", str(want_increasing)], (
        f"Expected 338204 for the random chain and {want_increasing} for dims 1..151; got {r.stdout.split()}.")
