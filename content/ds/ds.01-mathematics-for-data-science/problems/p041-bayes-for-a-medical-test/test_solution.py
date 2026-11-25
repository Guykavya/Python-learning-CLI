import math

import numpy as np
import pytest

from solution import bayes_posterior


def test_the_classic_case():
    assert bayes_posterior(0.01, 0.99, 0.05) == pytest.approx(99 / 594), "1% prior, 99% sensitivity, 5% false positives: 99 / (99 + 495)."


def test_edges_of_the_prior():
    assert bayes_posterior(0.0, 0.99, 0.05) == 0.0, "if nobody is sick a positive test cannot change that."
    assert bayes_posterior(1.0, 0.99, 0.05) == pytest.approx(1.0), "if everybody is sick, a positive test is right."


def test_a_perfect_test():
    assert bayes_posterior(0.01, 1.0, 0.0) == pytest.approx(1.0), "no false positives: a positive test is certain."


def test_higher_prior_gives_higher_posterior():
    vals = [bayes_posterior(p, 0.9, 0.1) for p in (0.01, 0.05, 0.2, 0.5, 0.9)]
    assert vals == sorted(vals), "a more common disease makes a positive test more convincing."


def test_symmetric_test_at_fifty_fifty():
    assert bayes_posterior(0.5, 0.8, 0.2) == pytest.approx(0.8), "with prior 0.5 and a symmetric test the posterior equals the sensitivity."


def test_impossible_positive_raises():
    with pytest.raises(ValueError):
        bayes_posterior(0.0, 0.9, 0.0)
