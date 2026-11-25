import numpy as np
from solution import sample_means

POP = np.random.default_rng(1).exponential(100, 20_000)


def test_shape_and_all_values_case():
    m = sample_means(np.arange(10.0), 10, 3, np.random.default_rng(0))
    assert m.shape == (3,) and np.allclose(m, 4.5), "Drawing all 10 values without replacement always gives mean 4.5."


def test_reproducible_with_the_given_rng():
    a = sample_means(POP, 30, 50, np.random.default_rng(7))
    np.random.seed(123)
    b = sample_means(POP, 30, 50, np.random.default_rng(7))
    assert np.array_equal(a, b), "Same seed must give the same means: use only the rng argument, never the global np.random."
    c = sample_means(POP, 30, 50, np.random.default_rng(8))
    assert not np.array_equal(a, c), "A different seed must give different samples."


def test_centre_and_spread():
    m = sample_means(POP, 50, 2000, np.random.default_rng(2))
    assert abs(m.mean() - POP.mean()) < 0.02 * POP.mean(), "The mean of the sample means is the population mean (within 2%)."
    expected = POP.std() / np.sqrt(50)
    assert abs(m.std() - expected) < 0.15 * expected, "The spread of the sample means is about sigma / sqrt(n)."


def test_no_replacement():
    pop = np.array([1.0, 1.0, 1.0, 1.0, 100.0])
    m = sample_means(pop, 5, 4, np.random.default_rng(0))
    assert np.allclose(m, pop.mean()), "Without replacement a sample of the whole population is the population."
