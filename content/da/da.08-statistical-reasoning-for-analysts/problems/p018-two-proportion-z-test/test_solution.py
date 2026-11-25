import pytest
from solution import two_prop_test
from statsmodels.stats.proportion import proportions_ztest


@pytest.mark.parametrize("kA,nA,kB,nB", [(115, 1000, 100, 1000), (30, 200, 55, 400), (80, 500, 50, 500), (5, 40, 12, 60)])
def test_matches_statsmodels(kA, nA, kB, nB):
    z, p = two_prop_test(kA, nA, kB, nB)
    z0, p0 = proportions_ztest([kA, kB], [nA, nB])
    assert z == pytest.approx(z0, abs=1e-9), "Pooled SE: sqrt(p(1-p)(1/nA + 1/nB)) with p = (kA + kB) / (nA + nB). A minus B."
    assert p == pytest.approx(p0, abs=1e-9), "Two-sided p-value: 2 * (1 - Phi(|z|))."


def test_identical_groups():
    assert two_prop_test(50, 500, 50, 500) == (0.0, 1.0), "Identical groups: z = 0 and p = 1."


def test_hand_example():
    z, p = two_prop_test(115, 1000, 100, 1000)
    assert z == pytest.approx(1.083, abs=0.002) and p == pytest.approx(0.279, abs=0.002)


def test_sign():
    z, _ = two_prop_test(10, 100, 20, 100)
    assert z < 0, "z is positive when A is higher than B, negative otherwise."


def test_zero_standard_error():
    assert two_prop_test(0, 100, 0, 100) == (0.0, 1.0), "No successes anywhere: SE = 0; return (0.0, 1.0)."
