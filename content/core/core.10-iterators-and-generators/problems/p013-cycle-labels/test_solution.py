from solution import cycle_labels


def test_repeats_in_order():
    assert cycle_labels(["red", "green", "blue"], 7) == ["red", "green", "blue", "red", "green", "blue", "red"], "Keep repeating the pattern until you have n items."


def test_single_label():
    assert cycle_labels(["a"], 3) == ["a", "a", "a"], "One label repeats."


def test_zero_and_empty():
    assert cycle_labels(["a", "b"], 0) == [], "n = 0 gives an empty list."
    assert cycle_labels([], 5) == [], "No labels, nothing to repeat."


def test_shorter_than_labels():
    assert cycle_labels([1, 2, 3, 4], 2) == [1, 2], "If n is smaller than the pattern, you get a prefix."


def test_accepts_iterator():
    assert cycle_labels(iter("xy"), 5) == ["x", "y", "x", "y", "x"], "labels may be any iterable, not only a list."
