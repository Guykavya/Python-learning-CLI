import math

import numpy as np
import pytest

from solution import cosine_similarity


def test_three_landmark_angles():
    assert cosine_similarity([1, 0], [2, 0]) == pytest.approx(1.0), "same direction (any length) gives 1."
    assert cosine_similarity([1, 0], [0, 5]) == pytest.approx(0.0, abs=1e-12), "perpendicular vectors give 0."
    assert cosine_similarity([1, 1], [-1, -1]) == pytest.approx(-1.0), "opposite direction gives -1."


def test_scale_does_not_matter():
    a, b = np.array([1.0, 2.0, 3.0]), np.array([3.0, -1.0, 2.0])
    base = cosine_similarity(a, b)
    assert cosine_similarity(10 * a, 0.5 * b) == pytest.approx(base), "scaling a vector must not change the cosine: divide by BOTH lengths."


def test_known_value():
    assert cosine_similarity([1, 0], [1, 1]) == pytest.approx(1 / math.sqrt(2)), "45 degrees: cos = 0.7071."


def test_zero_vector_raises_with_message():
    with pytest.raises(ValueError, match="zero vector"):
        cosine_similarity([0, 0], [1, 2])
    with pytest.raises(ValueError, match="zero vector"):
        cosine_similarity([1, 2], [0, 0])


def test_against_numpy_on_random_data():
    rng = np.random.default_rng(2)
    for _ in range(20):
        a, b = rng.normal(size=6), rng.normal(size=6)
        ref = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
        assert cosine_similarity(a, b) == pytest.approx(ref, rel=1e-9), "random vectors: dot / (|a| |b|)."
