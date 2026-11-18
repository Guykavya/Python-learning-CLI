import random
from functools import cmp_to_key
from itertools import permutations

from solution import largest_number


def brute(nums):
    return str(max(int("".join(str(x) for x in p)) for p in permutations(nums)))


def test_chapter_examples():
    assert largest_number([3, 30, 34, 5, 9]) == "9534330", (
        "Expected '9534330'. Plain descending text sort gives '9534303' because '30' > '3' as text; "
        "compare the two concatenations a + b and b + a instead.")
    assert largest_number([10, 2]) == "210", "Expected '210'. Sorting as numbers puts 10 first and gives '102'."


def test_zeros():
    assert largest_number([0, 0]) == "0", "All zeros: the answer is '0', not '00'."
    assert largest_number([0]) == "0", "A single 0: '0' (do not strip it away to an empty string)."
    assert largest_number([0, 1]) == "10", "Expected '10'."


def test_returns_a_string():
    out = largest_number([1, 2])
    assert isinstance(out, str), f"Return a string, not {type(out).__name__}."
    assert out == "21", "Expected '21'."


def test_tricky_prefixes():
    assert largest_number([121, 12]) == "12121", "'12' + '121' = '12121' beats '121' + '12' = '12112'."
    assert largest_number([824, 8247]) == "8248247", "'824' + '8247' beats '8247' + '824'."
    assert largest_number([3, 30]) == "330", "'3' + '30' = '330' beats '303'."


def test_input_not_changed():
    nums = [3, 30, 34]
    largest_number(nums)
    assert nums == [3, 30, 34], "Do not sort the caller's list in place."


def test_random_against_permutations():
    rng = random.Random(28)
    for _ in range(300):
        nums = [rng.choice([0, rng.randint(0, 9), rng.randint(0, 130)]) for _ in range(rng.randint(1, 6))]
        want = brute(nums)
        got = largest_number(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want!r} (every order tried), got {got!r}. Put a before b when "
            "str(a) + str(b) > str(b) + str(a); return '0' when everything is 0.")


def test_large_input():
    rng = random.Random(2828)
    nums = [rng.randint(0, 10**9) for _ in range(1000)]
    out = largest_number(nums)
    assert len(out) == sum(len(str(x)) for x in nums), "1000 numbers: every digit must appear exactly once."
    def compare(a, b):
        return -1 if a + b > b + a else (1 if a + b < b + a else 0)
    pieces = sorted((str(x) for x in nums), key=cmp_to_key(compare))
    assert out == "".join(pieces), "1000 random numbers: not the largest arrangement."
