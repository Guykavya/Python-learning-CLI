from solution import drop_negatives


def test_example_and_alias():
    data = [3, -1, 4, -5, 0, -9]
    alias = data
    result = drop_negatives(data)
    assert data == [3, 4, 0], (
        "The caller's list did not change. `numbers = [...]` rebinds the local name only; "
        "use slice assignment numbers[:] = [...].")
    assert alias is data and alias == [3, 4, 0]
    assert result is None, "Return None from an in-place function."


def test_adjacent_negatives():
    data = [-1, -2, -3, 5, -4, -6]
    drop_negatives(data)
    assert data == [5], (
        "Some negatives survived. Removing items while looping over the same list skips the next item.")


def test_all_negative():
    data = [-1, -1]
    drop_negatives(data)
    assert data == []


def test_nothing_to_remove():
    data = [0, 1, 2]
    drop_negatives(data)
    assert data == [0, 1, 2], "0 is not negative; keep it."


def test_empty():
    data = []
    drop_negatives(data)
    assert data == []
