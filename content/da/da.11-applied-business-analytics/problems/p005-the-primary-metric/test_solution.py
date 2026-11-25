import numpy as np
import pandas as pd
import pytest

from statsmodels.stats.proportion import proportions_ztest

from solution import two_prop


def test_chapter_style_example():
    r = two_prop(720, 12000, 790, 12000)
    assert r["A"] == pytest.approx(0.06) and r["B"] == pytest.approx(790 / 12000), "rates kA/nA and kB/nB."
    assert r["diff"] == pytest.approx(0.0058333, abs=1e-6) and r["rel_lift"] == pytest.approx(0.0972222, abs=1e-6)
    assert (round(r["lo"], 4), round(r["hi"], 4)) == (-0.0003, 0.0120), f"95% CI of the difference: -0.0003 to 0.0120 (unpooled standard error), got {r['lo']:.4f} to {r['hi']:.4f}"


@pytest.mark.parametrize("kA,nA,kB,nB", [(720, 12000, 790, 12000), (100, 2000, 130, 2100), (50, 1000, 30, 1100)])
def test_p_matches_statsmodels(kA, nA, kB, nB):
    r = two_prop(kA, nA, kB, nB)
    ref = proportions_ztest([kB, kA], [nB, nA])[1]
    assert r["p"] == pytest.approx(ref, abs=1e-9), f"p-value uses the pooled rate: expected {ref:.6f}, got {r['p']:.6f}"


def test_b_worse_gives_negative_lift():
    r = two_prop(50, 1000, 30, 1000)
    assert r["diff"] < 0 and r["rel_lift"] < 0 and r["hi"] < 0.0, "B converts less than A: negative difference, whole interval below 0."


def test_level_changes_the_interval():
    narrow, wide = two_prop(100, 2000, 130, 2000, level=0.90), two_prop(100, 2000, 130, 2000, level=0.99)
    assert narrow["hi"] - narrow["lo"] < wide["hi"] - wide["lo"], "a 99% interval is wider than a 90% one."


def test_plain_floats():
    assert all(type(v) is float for v in two_prop(10, 100, 20, 100).values()), "return plain floats."
