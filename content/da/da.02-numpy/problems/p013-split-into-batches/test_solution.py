import numpy as np
import pytest

from solution import batches


def as_lists(parts):
    return [p.tolist() for p in parts]


def test_example():
    got = batches(np.arange(10), 4)
    assert isinstance(got, list), f"return a Python list of arrays, got {type(got).__name__}."
    assert as_lists(got) == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]], (
        f"got {as_lists(got)}. np.split(x, 3) would fail here (10 is not divisible); the last batch is just shorter.")


def test_exact_multiple_has_no_empty_tail():
    got = batches(np.arange(8), 4)
    assert as_lists(got) == [[0, 1, 2, 3], [4, 5, 6, 7]], f"8 items in batches of 4: two batches, no empty third one. Got {as_lists(got)}."


def test_size_bigger_than_data():
    assert as_lists(batches(np.arange(3), 20)) == [[0, 1, 2]], "size 20 for 3 items: one batch with everything."
    assert as_lists(batches(np.arange(3), 3)) == [[0, 1, 2]], "size == len(x): one batch."


def test_size_one():
    assert as_lists(batches(np.arange(3), 1)) == [[0], [1], [2]], "size 1: one item per batch."


def test_empty_input():
    assert batches(np.arange(0), 3) == [], "no data, no batches: return []."


@pytest.mark.parametrize("size", [0, -1])
def test_bad_size(size):
    with pytest.raises(ValueError):
        batches(np.arange(5), size)


def test_batches_are_views():
    x = np.arange(10.0)
    got = batches(x, 3)
    for b in got:
        assert np.shares_memory(b, x), "every batch must be a view of x (a slice), not a copy: no np.array(...), .copy() or fancy indexing."
    got[1][0] = -1.0
    assert x[3] == -1.0, "writing into batch 1 must show in x[3]."


def test_rows_of_a_table():
    table = np.arange(14).reshape(7, 2)
    got = batches(table, 3)
    shapes = [b.shape for b in got]
    assert shapes == [(3, 2), (3, 2), (1, 2)], f"for a 2-D array, batch the ROWS and keep both columns; got shapes {shapes}."


@pytest.mark.parametrize("seed", range(5))
def test_random_sizes_rebuild_the_input(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(1, 60))
    size = int(rng.integers(1, 15))
    x = rng.normal(size=n)
    got = batches(x, size)
    assert len(got) == -(-n // size), f"{n} items in batches of {size} need {-(-n // size)} batches, got {len(got)}."
    assert all(len(b) == size for b in got[:-1]), "every batch except the last has exactly `size` items."
    np.testing.assert_array_equal(np.concatenate(got), x, err_msg="the batches joined together must give x back, in order.")
