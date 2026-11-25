import warnings

import numpy as np

from solution import zscore


def strict(*args, **kwargs):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        return zscore(*args, **kwargs)


EXAMPLE = np.array([[1.0, 10.0, 5.0], [2.0, 20.0, 5.0], [3.0, 30.0, 5.0]])


def test_the_example_columns():
    got = strict(EXAMPLE)
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.shape == (3, 3), f"the result keeps the shape of x, (3, 3); got {got.shape}."
    assert got.dtype == np.float64, f"the result must be float64, got {got.dtype}."
    s = np.sqrt(1.5)
    np.testing.assert_allclose(got, [[-s, -s, 0.0], [0.0, 0.0, 0.0], [s, s, 0.0]], rtol=1e-12, atol=1e-15,
                               err_msg="column z-scores of the example are wrong (mean and std along axis=0, population std).")


def test_constant_column_is_zero_without_warning():
    try:
        got = strict(EXAMPLE)
    except RuntimeWarning as w:
        raise AssertionError(f"a constant column raised a RuntimeWarning ({w}): divide by np.where(std == 0, 1.0, std).")
    assert not np.isnan(got).any(), "a constant column must become 0, not nan (0 / 0)."
    np.testing.assert_array_equal(got[:, 2], [0.0, 0.0, 0.0], err_msg="constant column -> zeros.")


def test_rows_with_axis_1():
    x = np.array([[1.0, 2.0, 3.0, 10.0], [4.0, 4.0, 4.0, 4.0], [0.0, 5.0, 0.0, 5.0]])
    got = strict(x, axis=1)
    assert got.shape == x.shape, f"axis=1 keeps the shape {x.shape}, got {got.shape}. Use keepdims=True so the (3, 1) means broadcast over rows."
    want = (x - x.mean(axis=1)[:, None]) / np.where(x.std(axis=1) == 0, 1, x.std(axis=1))[:, None]
    np.testing.assert_allclose(got, want, rtol=1e-12, atol=1e-15, err_msg="axis=1 must standardise each ROW.")
    np.testing.assert_allclose(got.mean(axis=1), 0.0, atol=1e-12, err_msg="every row should now have mean 0.")


def test_ddof_is_used():
    x = np.array([[1.0, 4.0], [2.0, 8.0], [6.0, 0.0], [3.0, 3.0]])
    got = strict(x, ddof=1)
    want = (x - x.mean(axis=0)) / x.std(axis=0, ddof=1)
    np.testing.assert_allclose(got, want, rtol=1e-12, err_msg="ddof=1 means the SAMPLE std: pass ddof to .std().")
    np.testing.assert_allclose(got.std(axis=0, ddof=1), 1.0, rtol=1e-12, err_msg="with ddof=1 the sample std of each column is 1.")


def test_integers_and_lists():
    got = strict([[1, 100], [3, 300]])
    assert got.dtype == np.float64, f"integer input must give float64, got {got.dtype}."
    np.testing.assert_allclose(got, [[-1.0, -1.0], [1.0, 1.0]], rtol=1e-12, err_msg="[[1, 100], [3, 300]] -> [[-1, -1], [1, 1]].")


def test_one_dimensional_input():
    got = strict(np.array([2.0, 4.0, 6.0]))
    assert got.shape == (3,), f"a 1-D input gives a 1-D result of the same length, got shape {got.shape}."
    np.testing.assert_allclose(got, [-np.sqrt(1.5), 0.0, np.sqrt(1.5)], rtol=1e-12, err_msg="1-D input: standardise the whole vector.")


def test_input_is_not_changed():
    x = EXAMPLE.copy()
    strict(x)
    np.testing.assert_array_equal(x, EXAMPLE, err_msg="do not change the caller's array (no x -= mean in place).")


def test_random_tables():
    rng = np.random.default_rng(32)
    for _ in range(10):
        x = rng.normal(rng.uniform(-100, 100, size=4), rng.uniform(0.1, 50, size=4), size=(int(rng.integers(2, 50)), 4))
        got = strict(x)
        np.testing.assert_allclose(got.mean(axis=0), 0.0, atol=1e-10, err_msg="every column must have mean 0.")
        np.testing.assert_allclose(got.std(axis=0), 1.0, rtol=1e-10, err_msg="every column must have population std 1.")
        np.testing.assert_allclose(got, (x - x.mean(axis=0)) / x.std(axis=0), rtol=1e-12, atol=1e-12, err_msg="z = (x - mean) / std per column.")
