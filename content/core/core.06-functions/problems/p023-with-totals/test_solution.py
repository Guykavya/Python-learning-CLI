from solution import with_totals


def test_example():
    assert with_totals([[1, 2], [3, 4]]) == [[1, 2, 3], [3, 4, 7], [4, 6, 10]]


def test_input_and_rows_unchanged():
    g = [[1, 2], [3, 4]]
    row0 = g[0]
    with_totals(g)
    assert g == [[1, 2], [3, 4]], (
        "The caller's grid changed. A copy made with [:] is shallow: the inner rows are shared. "
        "Build new rows with row + [total].")
    assert row0 == [1, 2] and g[0] is row0


def test_result_rows_are_new():
    g = [[5]]
    r = with_totals(g)
    assert r == [[5, 5], [5, 5]]
    assert r[0] is not g[0], "The result's rows must be new lists, not the caller's rows."


def test_one_row():
    assert with_totals([[1, 2, 3]]) == [[1, 2, 3, 6], [1, 2, 3, 6]]


def test_negatives_and_floats():
    assert with_totals([[1.5, -1], [0, 2]]) == [[1.5, -1, 0.5], [0, 2, 2], [1.5, 1, 2.5]]


def test_empty():
    assert with_totals([]) == [], "An empty grid returns []."
