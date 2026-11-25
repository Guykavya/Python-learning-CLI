import math

import numpy as np
import pytest

from solution import project


def test_axis_examples():
    assert project([3, 4], [1, 0]) == pytest.approx([3, 0]), "the shadow of [3, 4] on the x-axis is [3, 0]."
    assert project([2, 0], [0, 3]) == pytest.approx([0, 0]), "perpendicular vectors project to zero."


def test_direction_need_not_be_unit_length():
    assert project([1, 1], [2, 0]) == pytest.approx([1, 0]), "d = [2, 0] is not unit length: divide by d.d, not by 1."
    assert project([1, 1], [10, 0]) == pytest.approx([1, 0]), "the projection must not depend on the length of d."


def test_residual_is_orthogonal_and_p_is_parallel():
    rng = np.random.default_rng(3)
    for _ in range(20):
        a, d = rng.normal(size=5), rng.normal(size=5)
        p = project(a, d)
        assert (a - p) @ d == pytest.approx(0, abs=1e-9), "a - p must be perpendicular to d."
        assert abs(np.dot(p, d)) == pytest.approx(np.linalg.norm(p) * np.linalg.norm(d)), "p must lie on the line through d."


def test_projecting_twice_changes_nothing():
    a, d = np.array([1.0, 5.0, -2.0]), np.array([2.0, 1.0, 1.0])
    p = project(a, d)
    assert project(p, d) == pytest.approx(p), "a vector already on the line projects to itself."


def test_zero_direction_raises():
    with pytest.raises(ValueError):
        project([1, 2], [0, 0])
