import numpy as np
import pandas as pd
import pytest

from conftest import lint_finding
from solution import make_finding

R1 = {"churn_before": 4.04, "churn_after": 5.68, "ontime_before": 91.98, "ontime_after": 79.81, "saved": 65.18, "saved_lo": 60.3,
      "saved_hi": 70.53, "rr": 2.904, "rr_lo": 2.712, "rr_hi": 3.094, "late_pts": 1.37, "late_pts_lo": 1.27, "late_pts_hi": 1.48}
R2 = {"churn_before": 3.21, "churn_after": 4.46, "ontime_before": 95.2, "ontime_after": 88.4, "saved": 41.7, "saved_lo": 33.2,
      "saved_hi": 50.9, "rr": 1.75, "rr_lo": 1.42, "rr_hi": 2.16, "late_pts": 0.88, "late_pts_lo": 0.61, "late_pts_hi": 1.12}


@pytest.mark.parametrize("R", [R1, R2])
def test_passes_the_linter(R):
    f = make_finding(R)
    assert lint_finding(f) == [], f"the finding must pass lint_finding, issues: {lint_finding(f)}"


@pytest.mark.parametrize("R", [R1, R2])
def test_headline_numbers_come_from_R(R):
    h = make_finding(R).headline
    for part in (f"{R['churn_before']:.1f}%", f"{R['churn_after']:.1f}%", f"{R['ontime_before']:.0f}%", f"{R['ontime_after']:.0f}%"):
        assert part in h, f"the headline must contain {part} (from R, not typed); headline: {h!r}"


@pytest.mark.parametrize("R", [R1, R2])
def test_impact_and_evidence_numbers(R):
    f = make_finding(R)
    impact = f"about {R['saved']:.0f} customers (range {R['saved_lo']:.0f} to {R['saved_hi']:.0f})"
    assert impact in f.impact, f"the impact must contain {impact!r}; got {f.impact!r}"
    rr = f"{R['rr']:.1f} times as often (95% CI {R['rr_lo']:.1f} to {R['rr_hi']:.1f})"
    pts = f"{R['late_pts']:.1f} points (95% CI {R['late_pts_lo']:.1f} to {R['late_pts_hi']:.1f})"
    assert any(rr in e for e in f.evidence), f"an evidence item must contain {rr!r}"
    assert any(pts in e for e in f.evidence), f"an evidence item must contain {pts!r}"


def test_text_changes_when_R_changes():
    assert make_finding(R1).render_markdown() != make_finding(R2).render_markdown(), "different numbers must give a different page."
    assert "4.0%" not in make_finding(R2).headline, "4.0% is R1's number: a typed number does not follow the data."
