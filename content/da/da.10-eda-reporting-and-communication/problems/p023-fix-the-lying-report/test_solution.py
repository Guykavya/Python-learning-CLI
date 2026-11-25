import numpy as np
import pandas as pd
import pytest

from conftest import lint_finding
from solution import build_report

R1 = {"churn_before": 4.04, "churn_after": 5.68, "ontime_before": 91.98, "ontime_after": 79.81, "saved": 65.18, "saved_lo": 60.3,
      "saved_hi": 70.53, "rr": 2.904, "rr_lo": 2.712, "rr_hi": 3.094, "late_pts": 1.37, "late_pts_lo": 1.27, "late_pts_hi": 1.48}
R2 = {"churn_before": 3.21, "churn_after": 4.46, "ontime_before": 95.2, "ontime_after": 88.4, "saved": 41.7, "saved_lo": 33.2,
      "saved_hi": 50.9, "rr": 1.75, "rr_lo": 1.42, "rr_hi": 2.16, "late_pts": 0.88, "late_pts_lo": 0.61, "late_pts_hi": 1.12}

R1["limitations"] = ["Observational data.", "Short window after the price change."]
R2["limitations"] = ["Observational data.", "One comparison group.", "Synthetic customers.", "The courier data are self-reported.", "Eleven weeks only."]


@pytest.mark.parametrize("R", [R1, R2])
def test_headline_follows_R(R):
    h = build_report(R).headline
    for part in (f"{R['churn_before']:.1f}%", f"{R['churn_after']:.1f}%"):
        assert part in h, f"the headline must contain {part} from R (a typed number does not follow the data): {h!r}"


@pytest.mark.parametrize("R", [R1, R2])
def test_impact_follows_R(R):
    want = f"about {R['saved']:.0f} customers (range {R['saved_lo']:.0f} to {R['saved_hi']:.0f})"
    assert want in build_report(R).impact, f"the impact must contain {want!r}: is the centre value typed by hand?"


@pytest.mark.parametrize("R", [R1, R2])
def test_same_rounding_for_estimate_and_interval(R):
    want = f"Customers with a recent late box leave {R['rr']:.1f} times as often (95% CI {R['rr_lo']:.1f} to {R['rr_hi']:.1f})."
    got = build_report(R).evidence[0]
    assert got == want, f"estimate and interval must use the same rounding (one decimal); expected {want!r}, got {got!r}"


def test_all_limitations_are_kept():
    assert build_report(R2).limitations == R2["limitations"], "five limitations in, five out: never drop doubts silently."


@pytest.mark.parametrize("R", [R1, R2])
def test_linter_is_clean(R):
    f = build_report(R)
    assert lint_finding(f) == [], f"lint_finding issues: {lint_finding(f)}"
