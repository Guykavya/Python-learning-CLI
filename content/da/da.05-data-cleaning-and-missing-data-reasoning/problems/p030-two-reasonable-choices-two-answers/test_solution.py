import numpy as np
import pandas as pd
import pytest

from solution import two_ways


def small():
    return pd.DataFrame({"city": list("XXXYYY"), "age": [25, 25, 50, 25, 35, 50],
                         "income": [100, np.nan, 300, np.nan, 200, 400]}, index=[7, 8, 9, 10, 11, 12])


def survey(seed, n=3000):
    """Young people earn less AND skip the income question more often (MAR); the cities differ in their age mix."""
    rng = np.random.default_rng(seed)
    city = rng.choice(["Agra", "Bhopal", "Chennai"], n)
    lo = {"Agra": 20, "Bhopal": 25, "Chennai": 35}
    hi = {"Agra": 45, "Bhopal": 55, "Chennai": 60}
    age = np.array([rng.integers(lo[c], hi[c]) for c in city])
    income = 20000 + 800 * (age - 20) + rng.normal(0, 3000, n)
    income[rng.random(n) < np.where(age < 30, 0.5, 0.1)] = np.nan
    return pd.DataFrame({"city": city, "age": age, "income": income})


def slow(df):
    """The same two answers with plain loops."""
    def band(a):
        return 0 if a < 30 else (1 if a < 45 else 2)
    obs = {b: [] for b in range(3)}
    for a, inc in zip(df["age"], df["income"]):
        if not np.isnan(inc):
            obs[band(a)].append(inc)
    med = {b: float(np.median(v)) if v else np.nan for b, v in obs.items()}
    a_vals, b_vals = {}, {}
    for c, a, inc in zip(df["city"], df["age"], df["income"]):
        a_vals.setdefault(c, [])
        b_vals.setdefault(c, [])
        if not np.isnan(inc):
            a_vals[c].append(inc)
        b_vals[c].append(inc if not np.isnan(inc) else med[band(a)])
    return ({c: float(np.mean(v)) for c, v in sorted(a_vals.items())},
            {c: float(np.nanmean(v)) for c, v in sorted(b_vals.items())})


def test_worked_example():
    r = two_ways(small())
    assert set(r) == {"complete", "filled", "max_diff"}, "the dict needs the keys complete, filled, max_diff."
    assert r["complete"].to_dict() == pytest.approx({"X": 200.0, "Y": 300.0}), "complete cases: X = (100+300)/2, Y = (200+400)/2."
    assert r["filled"].to_dict() == pytest.approx({"X": 500 / 3, "Y": 700 / 3}), (
        "band medians of the observed incomes: under 30 -> 100, 30-44 -> 200, 45+ -> 350. X = (100+100+300)/3, Y = (100+200+400)/3. "
        "Got %s." % r["filled"].to_dict())
    assert r["max_diff"] == pytest.approx(200 / 3), "max_diff = largest absolute gap over the cities (Y: 300 - 233.33)."


def test_series_names_and_index():
    r = two_ways(small())
    for k in ["complete", "filled"]:
        assert r[k].index.tolist() == ["X", "Y"], "the index is the sorted city names."
        assert r[k].name == "income", "name both Series 'income'."
    assert type(r["max_diff"]) is float, "max_diff is a plain float."


def test_band_edges_are_30_and_45():
    df = pd.DataFrame({"city": ["A"] * 6, "age": [29, 30, 44, 45, 29, 45],
                       "income": [10.0, 20.0, 30.0, 40.0, np.nan, np.nan]})
    r = two_ways(df)
    # the gaps are a 29-year-old (band median 10) and a 45-year-old (band median 40)
    assert r["filled"]["A"] == pytest.approx((10 + 20 + 30 + 40 + 10 + 40) / 6), (
        "age 29 is in the first band, 30 and 44 in the second, 45 in the third: bands are [0,30), [30,45), [45,...).")


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_matches_the_slow_computation_and_the_answers_differ(seed):
    df = survey(seed)
    r = two_ways(df)
    a, b = slow(df)
    assert r["complete"].to_dict() == pytest.approx(a), "complete cases must equal the plain-loop mean of the answered incomes per city."
    assert r["filled"].to_dict() == pytest.approx(b), "filled must equal the plain-loop mean after filling with the band median of OBSERVED incomes."
    assert r["max_diff"] > 500, (
        "young people skip the question more often, so the two ways must differ clearly (more than 500 in some city). Got %.0f." % r["max_diff"])
    assert (r["filled"] < r["complete"]).all(), "dropping the (poorer) young inflates every city's mean, so filling lowers it."


def test_input_not_changed():
    df = survey(1, 300)
    before = df.copy()
    two_ways(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame (fill on a copy)")
