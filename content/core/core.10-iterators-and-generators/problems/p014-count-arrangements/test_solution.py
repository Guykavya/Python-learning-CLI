from solution import count_arrangements


def test_abc_two():
    assert count_arrangements("abc", 2) == {"product": 9, "permutations": 6, "combinations": 3}, (
        "For 3 items and k=2: product 3*3=9, permutations 3*2=6, combinations 3. Check the repeat= argument of product."
    )


def test_k_zero():
    assert count_arrangements("abc", 0) == {"product": 1, "permutations": 1, "combinations": 1}, "k = 0 gives exactly one tuple: the empty tuple."


def test_k_larger_than_items():
    assert count_arrangements("ab", 3) == {"product": 8, "permutations": 0, "combinations": 0}, (
        "You cannot pick 3 different items out of 2, but product allows repeats: 2**3 = 8."
    )


def test_bigger():
    assert count_arrangements(range(5), 3) == {"product": 125, "permutations": 60, "combinations": 10}, "5 items, k=3: 125, 60 and 10."


def test_returns_plain_ints():
    r = count_arrangements("ab", 1)
    assert r == {"product": 2, "permutations": 2, "combinations": 2}, "One pick out of 2 items: 2 each."
    assert all(type(v) is int for v in r.values()), "The values are counts (int), not lists or iterators."
