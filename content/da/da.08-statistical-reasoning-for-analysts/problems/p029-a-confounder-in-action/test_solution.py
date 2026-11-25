import pandas as pd
import pytest
from solution import confounder_report


def test_small_hand_table():
    df = pd.DataFrame({"app": [True, True, False, False], "spend": [3000.0, 2800, 2500, 2300],
                       "engagement": [1.0, 0.0, -1.0, -0.5], "income": [0.5, 0.5, 0.0, 0.0]})
    r = confounder_report(df)
    assert r["naive_diff"] == pytest.approx(500.0), "App users 2,900 against others 2,400."
    assert r["engagement_gap"] == pytest.approx(1.25) and r["income_gap"] == pytest.approx(0.5), "Users minus others, for each variable."


def test_on_the_simulated_world(world_factory):
    w = world_factory(n=4000, tau=150, seed=60)
    r = confounder_report(w)
    assert set(r) == {"naive_diff", "engagement_gap", "income_gap"}, "Keys: naive_diff, engagement_gap, income_gap."
    assert r["naive_diff"] >= 1.5 * 150, "The naive difference is much larger than the true effect (150): the groups are different people."
    assert r["engagement_gap"] > 0.5 and r["income_gap"] > 0.2, "App users are more engaged and richer."
    g = w.groupby("app")["spend"].mean()
    assert r["naive_diff"] == pytest.approx(g[True] - g[False])
