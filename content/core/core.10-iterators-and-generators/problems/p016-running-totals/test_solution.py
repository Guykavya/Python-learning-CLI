from solution import running_max, running_totals


def test_totals():
    assert running_totals([1, 2, 3, 4]) == [1, 3, 6, 10], "Each output is the sum of all items so far."
    assert running_totals([]) == [], "Empty in, empty out."


def test_totals_negative_and_floats():
    assert running_totals([5, -2, -3]) == [5, 3, 0], "Negative numbers lower the running total."


def test_max():
    assert running_max([3, 1, 4, 1, 5]) == [3, 3, 4, 4, 5], "Each output is the biggest item so far."
    assert running_max([9, 2, 1]) == [9, 9, 9], "Once the maximum is reached it stays."
    assert running_max([]) == [], "Empty in, empty out."


def test_generator_input():
    assert running_totals(n for n in range(4)) == [0, 1, 3, 6], "Input may be a generator."
