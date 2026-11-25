import numpy as np

from solution import running_mean_of_flips


def test_shape_dtype_and_first_value():
    got = running_mean_of_flips(1000, np.random.default_rng(41))
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.shape == (1000,), f"one running mean per flip: shape (1000,), got {got.shape}."
    assert got.dtype == np.float64, f"proportions are float64, got {got.dtype} (integer division? cumsum alone?)."
    assert got[0] in (0.0, 1.0), f"the first running mean is the first flip itself, 0 or 1; got {got[0]}. Divide by 1, 2, 3, ..., not 0, 1, 2."
    assert np.all((got >= 0) & (got <= 1)), "a proportion of heads lies between 0 and 1."


def test_it_is_really_a_running_mean_of_zeros_and_ones():
    got = running_mean_of_flips(500, np.random.default_rng(1))
    heads = np.round(got * np.arange(1, 501)).astype(int)
    np.testing.assert_allclose(got * np.arange(1, 501), heads, atol=1e-9,
                               err_msg="value i times (i + 1) must be a whole number of heads: divide the running total by 1..n.")
    steps = np.diff(np.concatenate([[0], heads]))
    assert set(steps.tolist()) <= {0, 1}, "each flip adds 0 or 1 head: the running total may only grow by 0 or 1 per step (flips must be 0/1, not 1/2)."


def test_zero_flips():
    got = running_mean_of_flips(0, np.random.default_rng(1))
    assert got.shape == (0,), f"n = 0 gives an empty array, got shape {got.shape}."


def test_law_of_large_numbers_on_three_seeds():
    for seed in (1, 2, 3):
        got = running_mean_of_flips(100_000, np.random.default_rng(seed))
        assert abs(got[-1] - 0.5) < 0.02, (
            f"seed {seed}: after 100,000 fair flips the proportion of heads should be very close to 0.5, got {got[-1]:.4f}. "
            "integers(0, 2) gives 0 or 1; integers(0, 1) gives only 0.")


def test_reproducible_with_the_given_rng():
    np.random.seed(0)
    a = running_mean_of_flips(200, np.random.default_rng(9))
    np.random.seed(5)
    b = running_mean_of_flips(200, np.random.default_rng(9))
    np.testing.assert_array_equal(a, b, err_msg="same seed, same result, whatever np.random.seed says: use the rng you are given.")
    rng = np.random.default_rng(10)
    assert not np.array_equal(running_mean_of_flips(200, rng), running_mean_of_flips(200, rng)), (
        "two calls with the same rng gave the same flips: do not create a new default_rng inside the function.")
