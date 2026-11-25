import math

import numpy as np
import pytest

from solution import components_for


def _three_directions(seed=14):
    rng = np.random.default_rng(seed)
    Z = rng.normal(size=(400, 3)) * [10.0, 8.0, 6.0]
    Q = np.linalg.qr(rng.normal(size=(6, 3)))[0].T
    return Z @ Q + rng.normal(scale=0.1, size=(400, 6))


def test_three_strong_directions():
    X = _three_directions()
    assert components_for(X, 0.95) == 3, "three strong directions plus tiny noise: 3 components keep 95%."
    assert components_for(X, 0.5) <= 2, "half of the variance needs only one or two."


def test_share_one_returns_all_nonzero_variance_directions():
    rng = np.random.default_rng(15)
    X = rng.normal(size=(50, 2)) @ rng.normal(size=(2, 5))
    assert components_for(X, 1.0) == 2, "five columns but only two independent directions: k = 2 reaches 100% (watch rounding)."


def test_monotone_in_share():
    X = _three_directions(16)
    ks = [components_for(X, s) for s in (0.3, 0.6, 0.9, 0.99)]
    assert ks == sorted(ks), f"a higher target can never need fewer components, got {ks}."


def test_constant_shift_does_not_matter():
    X = _three_directions(17)
    assert components_for(X + 1000, 0.95) == components_for(X, 0.95), "centre the data first."


def test_isotropic_noise_needs_nearly_all():
    rng = np.random.default_rng(18)
    X = rng.normal(size=(1000, 6))
    assert components_for(X, 0.95) >= 5, "equal spread in every direction: no small set of components is enough."
