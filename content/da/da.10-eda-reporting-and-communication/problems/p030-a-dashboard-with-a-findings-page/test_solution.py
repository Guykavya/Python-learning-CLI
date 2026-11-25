import numpy as np
import pandas as pd
import pytest

from streamlit.testing.v1 import AppTest

from conftest import make_freshbox
from solution import baseline, filter_data, finding_text, monthly_kpis

ALL = (["organic", "paid", "referral"], ["2-meal", "3-meal"], ["Large", "Metro", "Small"])


def tiny():
    cus = pd.DataFrame({"customer_id": [1, 2, 3], "channel": ["paid", "organic", "paid"], "plan": ["2-meal"] * 3, "city": ["Metro"] * 3,
                        "last_week": pd.to_datetime(["2024-01-15", pd.NaT, "2024-02-05"])})
    pan = pd.DataFrame({"customer_id": [1, 1, 2, 2, 2, 3, 3, 3],
                        "week": pd.to_datetime(["2024-01-01", "2024-01-08", "2024-01-01", "2024-01-08", "2024-02-05", "2024-01-01", "2024-01-08", "2024-02-05"]),
                        "late": [False, True, False, False, False, False, False, True], "price": 599})
    return cus, pan


# ---------- the logic, without Streamlit


def test_filter_data():
    cus, pan = tiny()
    assert filter_data(cus, pan, [], ["2-meal"], ["Metro"]) is None, "an empty list means nothing selected: None."
    c, p = filter_data(cus, pan, ["paid"], ["2-meal"], ["Metro"])
    assert sorted(c["customer_id"]) == [1, 3] and len(p) == 5, "paid customers 1 and 3 with their 5 panel rows."
    assert filter_data(cus, pan, ["referral"], ["2-meal"], ["Metro"]) is None, "no matching panel rows: None."


def test_monthly_kpis():
    k = monthly_kpis(*tiny())
    assert list(k.columns) == ["opening_actives", "churned", "churn_rate_pct", "on_time_pct"], f"columns, got {list(k.columns)}"
    jan, feb = k.loc[pd.Period("2024-01")], k.loc[pd.Period("2024-02")]
    assert (jan["opening_actives"], jan["churned"]) == (3, 1) and jan["churn_rate_pct"] == pytest.approx(100 / 3)
    assert jan["on_time_pct"] == pytest.approx(500 / 6), "1 late box in 6 January rows."
    assert (feb["opening_actives"], feb["churned"]) == (2, 1), "February: customers 2 and 3 open it, 3 leaves."


def test_baseline_and_finding_text():
    k = pd.DataFrame({"churn_rate_pct": [4.0, 4.2, 6.5], "on_time_pct": [92.0, 91.0, 79.4]},
                     index=pd.PeriodIndex(["2024-04", "2024-05", "2024-12"], freq="M"))
    base = baseline(k, "2024-04", "2024-05")
    assert base == pytest.approx({"churn": 4.1, "on_time": 91.5}), f"means over the baseline months, got {base}"
    assert finding_text(k, base) == ("In 2024-12, monthly churn was 6.5% against 4.1% in the baseline period (+2.4 points); "
                                     "79% of boxes arrived on time against 92%."), f"got {finding_text(k, base)!r}"


# ---------- the app, with test data


def app():
    from conftest import make_freshbox
    from solution import main
    main(*make_freshbox(seed=3, n=400))


@pytest.fixture(scope="module")
def data():
    return make_freshbox(seed=3, n=400)


def churn_tile(at):
    tiles = [m for m in at.metric if m.label.startswith("Monthly churn")]
    return tiles[0].value if tiles else None


def test_default_view_matches_the_logic(data):
    at = AppTest.from_function(app, default_timeout=60).run()
    assert not at.exception, f"the app raised: {[e.value for e in at.exception]}"
    assert at.title[0].value == "FreshBox: churn dashboard"
    assert [m.label for m in at.sidebar.multiselect] == ["Channel", "Plan", "City"], "three filters in the sidebar."
    assert [t.label for t in at.tabs] == ["Findings", "Explore"], "two tabs: Findings and Explore."
    k = monthly_kpis(*data)
    last = k.index[-1]
    assert [m.label for m in at.metric] == [f"Opening actives, {last}", f"Monthly churn, {last}", f"Boxes on time, {last}"], f"metric labels, got {[m.label for m in at.metric]}"
    assert churn_tile(at) == f"{k['churn_rate_pct'].iloc[-1]:.1f}%", "the churn tile must equal the logic's KPI for the last month."
    assert at.metric[0].value == f"{int(k['opening_actives'].iloc[-1]):,}"
    assert finding_text(k, baseline(k)) in [m.value for m in at.markdown], "the Findings tab shows finding_text(...)."


def test_a_filter_changes_the_numbers(data):
    at = AppTest.from_function(app, default_timeout=60).run()
    at.sidebar.multiselect[0].set_value(["paid"]).run()
    sel = filter_data(*data, ["paid"], ALL[1], ALL[2])
    k = monthly_kpis(*sel)
    assert churn_tile(at) == f"{k['churn_rate_pct'].iloc[-1]:.1f}%", "after filtering to paid, the tile must equal the logic on paid customers."


def test_empty_selection_shows_a_warning():
    at = AppTest.from_function(app, default_timeout=60).run()
    at.sidebar.multiselect[1].set_value([]).run()
    assert not at.exception, "an empty filter must not crash the app."
    assert [w.value for w in at.warning] == ["Select at least one value in every filter."]
    assert len(at.metric) == 0, "no KPI tiles for an empty selection."


@pytest.mark.parametrize("ch,pl,ci", [(["referral"], ["2-meal"], ["Small"]), (["organic"], ["3-meal"], ["Large", "Metro"]), (ALL[0], ["2-meal"], ["Metro"])])
def test_smoke_grid(ch, pl, ci):
    at = AppTest.from_function(app, default_timeout=60).run()
    at.sidebar.multiselect[0].set_value(ch)
    at.sidebar.multiselect[1].set_value(pl)
    at.sidebar.multiselect[2].set_value(ci)
    at.run()
    assert not at.exception, f"no combination of filters may crash the app: {ch}, {pl}, {ci}"
    assert at.warning or churn_tile(at), "either a warning or the KPI tiles."
