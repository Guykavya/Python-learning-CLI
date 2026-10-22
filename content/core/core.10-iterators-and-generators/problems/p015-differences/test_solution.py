from solution import differences


def test_basic():
    assert differences([1, 4, 9, 16]) == [3, 5, 7], "Each item minus the one before it."
    assert differences([5, 3, 3, 10]) == [-2, 0, 7], "Negative and zero differences count too: later minus earlier."


def test_short_inputs():
    assert differences([7]) == [], "One number has no neighbour."
    assert differences([]) == [], "No numbers, no differences."


def test_generator_input():
    assert differences(n * n for n in range(5)) == [1, 3, 5, 7], "Input may be a generator: do not index into it."
