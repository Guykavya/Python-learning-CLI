import numpy as np

from solution import simulate_rolls


def test_shape_dtype_and_total():
    got = simulate_rolls(600, np.random.default_rng(123))
    assert isinstance(got, np.ndarray), f"return a NumPy array, not a {type(got).__name__}."
    assert got.shape == (6,), f"one count per face 1..6: shape (6,), got {got.shape}. With bincount, did you keep the count of 0s?"
    assert np.issubdtype(got.dtype, np.integer), f"counts are integers, got {got.dtype}."
    assert int(got.sum()) == 600, f"the counts must add up to n = 600, got {int(got.sum())}."


def test_zero_rolls():
    got = simulate_rolls(0, np.random.default_rng(1))
    assert got.shape == (6,) and int(got.sum()) == 0, f"n = 0 gives six zeros, got {got!r}."


def test_faces_one_to_six_are_all_used():
    got = simulate_rolls(60_000, np.random.default_rng(38))
    assert np.all(got > 9_000) and np.all(got < 11_000), (
        f"60,000 fair rolls give about 10,000 per face; got {got.tolist()}. "
        "integers(1, 7) excludes 7: integers(1, 6) never rolls a 6, integers(0, 6) rolls 0s.")


def test_same_seed_same_counts():
    a = simulate_rolls(1000, np.random.default_rng(7))
    b = simulate_rolls(1000, np.random.default_rng(7))
    np.testing.assert_array_equal(a, b, err_msg="two generators with the same seed must give the same counts: use the rng you are given.")


def test_global_seed_does_not_matter():
    np.random.seed(0)
    a = simulate_rolls(1000, np.random.default_rng(11))
    np.random.seed(999)
    b = simulate_rolls(1000, np.random.default_rng(11))
    np.testing.assert_array_equal(a, b, err_msg=("the result changed with np.random.seed: you used the hidden global generator "
                                                 "(np.random.randint / np.random.seed). Use rng.integers (Ch. 13.6)."))


def test_the_generator_moves_on():
    rng = np.random.default_rng(5)
    a = simulate_rolls(1000, rng)
    b = simulate_rolls(1000, rng)
    assert not np.array_equal(a, b), ("two calls with the SAME rng gave identical counts: did you create a new "
                                      "default_rng(seed) inside the function? Draw from the rng that is passed in.")


def test_different_seeds_differ():
    a = simulate_rolls(1000, np.random.default_rng(1))
    b = simulate_rolls(1000, np.random.default_rng(2))
    assert not np.array_equal(a, b), "different seeds should give different rolls: is the rng ignored?"
