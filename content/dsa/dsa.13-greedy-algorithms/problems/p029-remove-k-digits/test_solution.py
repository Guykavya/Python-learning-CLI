import pathlib
import random
import subprocess
import sys
from itertools import combinations

from solution import remove_k_digits

HERE = pathlib.Path(__file__).parent


def brute(num, k):
    """Try every choice of digits to keep (in order) and take the smallest value."""
    keep = len(num) - k
    if keep == 0:
        return "0"
    best = min(int("".join(num[i] for i in idx)) for idx in combinations(range(len(num)), keep))
    return str(best)


def test_chapter_examples():
    assert remove_k_digits("1432219", 3) == "1219", (
        "Expected '1219': pop 4, 3 and the second 2 because a smaller digit follows each of them.")
    assert remove_k_digits("10200", 1) == "200", "Expected '200': remove the 1, then strip the leading zero."
    assert remove_k_digits("10", 2) == "0", "Everything removed: return '0', not ''."
    assert remove_k_digits("12345", 2) == "123", (
        "Expected '123'. The digits only rise, so nothing is popped: the leftover removals come off the RIGHT end.")


def test_k_zero():
    assert remove_k_digits("4321", 0) == "4321", "k = 0: remove nothing."


def test_equal_digits_are_not_popped():
    assert remove_k_digits("1121", 1) == "111", (
        "Expected '111'. Pop only when the top is STRICTLY bigger: popping an equal 1 gives '121'.")
    assert remove_k_digits("2221", 1) == "221", "Expected '221'."


def test_only_zeros_left():
    assert remove_k_digits("100", 1) == "0", "'100' minus the 1 is '00', which is written '0'."
    assert remove_k_digits("9", 1) == "0", "Remove the only digit: '0'."


def test_random_against_brute_force():
    rng = random.Random(29)
    for _ in range(600):
        n = rng.randint(1, 8)
        num = str(rng.randint(1, 9)) + "".join(rng.choice("0123456789" if rng.random() < 0.5 else "0011223")
                                               for _ in range(n - 1))
        k = rng.randint(0, n)
        want = brute(num, k)
        got = remove_k_digits(num, k)
        assert got == want, (
            f"num={num!r}, k={k}: expected {want!r} (every choice tried), got {got!r}. Pop while the top is bigger "
            "than the next digit; leftover removals from the right; strip leading zeros; '0' if empty.")


def test_large_input_is_linear():
    code = (
        "from solution import remove_k_digits\n"
        "n = 10**5\n"
        "a = remove_k_digits('1' * (n // 2) + '9' * (n // 2), n // 2)\n"
        "b = remove_k_digits('9' * (n // 2) + '1' * (n // 2), n // 2)\n"
        "print(a == '1' * (n // 2), b == '1' * (n // 2))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100,000 digits with k = 50,000. Deleting one digit at a time is O(n k); "
        "use the stack so each digit is pushed and popped at most once.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["True", "True"], (
        f"100,000 digits: removing half of '1...19...9' or '9...91...1' should leave 50,000 ones; got {r.stdout.split()}.")
