import pytest

from solution import budget, burn_alerts, burn_rate


def test_budget_numbers():
    got = budget(0.999, total=1_000_000, failed=400)
    assert got["allowed_failures"] == pytest.approx(1000.0), "0.1% of a million requests may fail: 1000."
    assert got["remaining_failures"] == pytest.approx(600.0)
    assert got["remaining_share"] == pytest.approx(0.6)
    assert got["exhausted"] is False


def test_budget_overspent():
    got = budget(0.99, total=10_000, failed=250)
    assert got["allowed_failures"] == pytest.approx(100.0)
    assert got["remaining_failures"] == pytest.approx(-150.0), "Overspent: negative remaining failures."
    assert got["remaining_share"] == pytest.approx(-1.5), "Remaining share is below 0 when the budget is overspent."
    assert got["exhausted"] is True


def test_budget_exactly_spent_is_not_exhausted():
    got = budget(0.99, total=10_000, failed=100)
    assert got["remaining_share"] == pytest.approx(0.0) and got["exhausted"] is False, \
        "Exactly on budget: remaining share 0.0, and not exhausted yet (exhausted means failed > allowed)."


def test_budget_with_no_traffic():
    got = budget(0.999, 0, 0)
    assert got == {"allowed_failures": 0.0, "remaining_failures": 0.0, "remaining_share": 1.0, "exhausted": False}, \
        "No requests: nothing allowed, nothing spent; the share is 1.0 (not a ZeroDivisionError)."


def test_the_chapters_budget_in_minutes():
    allowed = budget(0.999, total=30 * 24 * 60, failed=0)["allowed_failures"]
    assert allowed == pytest.approx(43.2), "99.9% of 30 days of minutes: 43.2 minutes (chapter 10.7)."


def test_burn_rate_values():
    assert burn_rate(0.999, 10_000, 150) == pytest.approx(15.0), "1.5% failing against a 0.1% budget: 15 times too fast."
    assert burn_rate(0.999, 10_000, 10) == pytest.approx(1.0), "Failing at exactly the budget rate: burn rate 1."
    assert burn_rate(0.999, 10_000, 0) == 0.0


def test_burn_rate_with_no_traffic():
    assert burn_rate(0.999, 0, 0) == 0.0, "No traffic, no burn."


def test_burn_rate_is_rounded_so_thresholds_work():
    assert burn_rate(0.999, 100_000, 1440) == 14.4, "1.44% against 0.1% is 14.4: round to 9 decimals so that '>= 14.4' fires at exactly the threshold."


def test_fast_burn():
    assert burn_alerts(0.999, {"1h": (10_000, 150), "6h": (60_000, 60)}) == ["fast-burn"], "15x in the last hour: fast burn only."


def test_fast_burn_threshold_is_inclusive():
    assert burn_alerts(0.999, {"1h": (100_000, 1440), "6h": (600_000, 0)}) == ["fast-burn"], "Exactly 14.4 fires."
    assert burn_alerts(0.999, {"1h": (100_000, 1439), "6h": (600_000, 0)}) == [], "Just below 14.4 does not."


def test_slow_burn():
    assert burn_alerts(0.999, {"1h": (10_000, 20), "6h": (60_000, 400)}) == ["slow-burn"], \
        "A steady leak: 0.67% over six hours is a burn rate of 6.67, at least 6.0."
    assert burn_alerts(0.999, {"1h": (10_000, 20), "6h": (60_000, 359)}) == [], "358 would be... below 6.0: no page."


def test_both_rules_in_order():
    assert burn_alerts(0.999, {"1h": (10_000, 500), "6h": (60_000, 3000)}) == ["fast-burn", "slow-burn"], "List fast-burn first, then slow-burn."


def test_quiet_system_does_not_page():
    assert burn_alerts(0.999, {"1h": (50_000, 20), "6h": (300_000, 150)}) == [], "A few errors within the budget do not page a human."


def test_windows_without_traffic():
    assert burn_alerts(0.999, {"1h": (0, 0), "6h": (0, 0)}) == []


def test_missing_window_key():
    with pytest.raises(ValueError):
        burn_alerts(0.999, {"1h": (10, 0)})


@pytest.mark.parametrize("call", [
    lambda: budget(1.0, 10, 0), lambda: budget(0, 10, 0), lambda: budget(0.99, 10, 11), lambda: budget(0.99, -1, 0),
    lambda: burn_rate(1.5, 10, 0), lambda: burn_rate(0.99, 10, -1),
])
def test_bad_input(call):
    with pytest.raises(ValueError):
        call()
