import math

import numpy as np
import pytest

from solution import sequential_posterior


def test_one_positive_matches_bayes():
    assert sequential_posterior(0.01, [True]) == pytest.approx(99 / 594), "one positive test: the posterior of problem 41."


def test_two_positives_raise_it_more():
    one = sequential_posterior(0.01, [True])
    two = sequential_posterior(0.01, [True, True])
    assert two > one, "a second positive must raise the probability further."
    assert two == pytest.approx(0.7984, abs=1e-3), "the posterior of the first test is the prior of the second."


def test_a_negative_lowers_it():
    pos = sequential_posterior(0.01, [True])
    both = sequential_posterior(0.01, [True, False])
    assert both < pos, "a negative result is evidence against the disease: use (1 - sensitivity) and (1 - false positive rate)."
    assert both < 0.01, "one positive and one negative leave the probability below the 1% prior here."


def test_empty_list_and_order_does_not_matter():
    assert sequential_posterior(0.3, []) == 0.3, "no tests, no update."
    a = sequential_posterior(0.1, [True, False, True])
    b = sequential_posterior(0.1, [False, True, True])
    assert a == pytest.approx(b), "independent results can be applied in any order."


def test_matches_the_odds_form():
    prior, sens, fpr = 0.05, 0.9, 0.2
    odds = prior / (1 - prior) * (sens / fpr) ** 2 * ((1 - sens) / (1 - fpr))
    assert sequential_posterior(prior, [True, True, False], sens, fpr) == pytest.approx(odds / (1 + odds)), "posterior odds = prior odds times one likelihood ratio per result."
