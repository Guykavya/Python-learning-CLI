import numpy as np
import pandas as pd
import pytest

import re

from conftest import make_data
from solution import Finding, build_case_study, check_case_study, lint_finding

SEGS = ["Champions", "Loyal", "New / promising", "Needs attention", "At risk", "Hibernating"]


def independent(data):
    """The numbers of the page, computed again with plain code."""
    exp, ses, cus, orders, asof = data["exp"], data["sessions"], data["customers"], data["orders"], data["asof"]
    a, b = exp[exp["variant"] == "A"]["converted"], exp[exp["variant"] == "B"]["converted"]
    pA, pB, nA, nB = a.mean(), b.mean(), len(a), len(b)
    se = np.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB)
    diff = (pB - pA) * 100
    ab = f"{diff:+.2f} points (95% CI {diff - 1.959964 * se * 100:+.2f} to {diff + 1.959964 * se * 100:+.2f})"
    rate = lambda dev: ses[(ses["device"] == dev) & ses["added_to_cart"]]["started_checkout"].mean() * 100
    fun = f"{rate('mobile'):.0f}% against {rate('desktop'):.0f}%"
    repeat = {}
    for ch, sub in cus.groupby("channel"):
        ok = 0
        eligible = sub[sub["first_order"] <= asof - pd.Timedelta(days=90)]
        for cid, first in zip(eligible["customer_id"], eligible["first_order"]):
            dates = sorted(orders.loc[orders["customer_id"] == cid, "order_date"])
            ok += len(dates) > 1 and (dates[1] - first).days <= 90
        repeat[ch] = ok / len(eligible) * 100
    return ab, fun, repeat


@pytest.fixture(scope="module")
def case():
    data = make_data(seed=0)
    return data, build_case_study(data)


def test_returns_finding_page_results(case):
    data, (finding, page, results) = case
    assert isinstance(finding, Finding) and isinstance(page, str) and isinstance(results, dict), "return (Finding, str, dict)."
    for key in ("expected", "decimals", "ab", "funnel", "repeat", "segments"):
        assert key in results, f"results needs the key {key!r}."


def test_the_finding_passes_the_linter(case):
    _, (finding, _, _) = case
    assert lint_finding(finding) == [], f"lint_finding must find no problems, got {lint_finding(finding)}"


def test_numbers_are_the_computed_ones(case):
    data, (finding, page, results) = case
    ab, fun, repeat = independent(data)
    assert results["ab"] == ab and ab in page, f"A/B text should be {ab!r}, got {results['ab']!r}"
    assert results["funnel"] == fun and fun in page, f"funnel text should be {fun!r}, got {results['funnel']!r}"
    for ch, r in repeat.items():
        assert f"{ch}: {r:.1f}%" in page, f"the page needs the line '{ch}: {r:.1f}%' (90-day repeat rate of the {ch} customers)."
    assert list(results["repeat"]) == sorted(repeat), "channels sorted."
    assert finding.headline.count(fun.split(" against ")[0]) >= 1 and fun.split(" against ")[1] in finding.headline, "the headline states the funnel numbers."


def test_segments_cover_all_customers_in_order(case):
    data, (_, page, results) = case
    assert list(results["segments"]) == SEGS, "segments in the order of SEGMENTS."
    n_customers = data["orders"]["customer_id"].nunique()
    assert sum(results["segments"].values()) == n_customers, "every customer with an order gets exactly one segment."
    assert all(f"{s}: {n:,}" in page for s, n in results["segments"].items()), "one line per segment on the page."


def test_expected_list_and_decimals(case):
    _, (_, page, results) = case
    assert results["expected"][:2] == [results["ab"], results["funnel"]], "expected starts with the A/B text and the funnel text."
    assert all(text in page for text in results["expected"]), "every expected string is on the page."
    assert results["decimals"] == sorted(set(re.findall(r"[+-]?\d[\d,]*\.\d+", page))), "decimals: the sorted decimal numbers of the page."


def test_a_second_data_set_changes_the_numbers(case):
    _, (_, page1, _) = case
    data2 = make_data(seed=5, lift=0.0, gap=0.05)
    finding2, page2, results2 = build_case_study(data2)
    ab2, fun2, repeat2 = independent(data2)
    assert page2 != page1, "different data must give a different page (no hard-coded numbers)."
    assert ab2 in page2 and fun2 in page2, f"the second page needs {ab2!r} and {fun2!r}."
    assert lint_finding(finding2) == [], "the finding stays clean for other data."


def test_check_accepts_the_page_and_catches_edits(case):
    _, (_, page, results) = case
    assert check_case_study(page, results) == [], f"an untouched page has no problems, got {check_case_study(page, results)}"
    fun = results["funnel"]
    edited = page.replace(fun, "99% against 11%")
    problems = check_case_study(edited, results)
    assert problems[0] == f"missing: {fun}", f"first the missing expected string, got {problems}"
    assert "number not in the results" not in problems[0]
    padded = page + "\n- Extra claim: 12.7% growth"
    assert check_case_study(padded, results) == ["number not in the results: 12.7"], "a decimal number nobody computed is reported once."
