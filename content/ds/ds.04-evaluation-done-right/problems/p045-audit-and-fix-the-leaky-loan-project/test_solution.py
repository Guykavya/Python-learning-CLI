import pytest

from conftest import make_loans
from solution import audit


@pytest.fixture(scope="module", params=[3, 4])
def result(request):
    df = make_loans(3000, 300, seed=request.param, n_vendor=20)
    return df, audit(df)


def test_keys(result):
    _, r = result
    assert set(r) == {"leaky_column", "duplicate_rows", "group_column", "leaky_auc", "honest_auc"}, "return exactly the five documented keys."


def test_the_target_leak_is_found(result):
    _, r = result
    assert r["leaky_column"] == "collections_calls", "collections calls happen AFTER a default; the single-feature check (AUC about 0.97 alone) must find it."


def test_duplicates_and_groups(result):
    df, r = result
    assert r["duplicate_rows"] == 180, "the faulty import loaded 6% of 3,000 loans twice: 180 repeated loan_id rows."
    assert r["group_column"] == "customer_id", "customers have several loans: customer_id is the group to split by."


def test_the_two_scores(result):
    _, r = result
    assert r["leaky_auc"] > 0.9, f"the colleague's evaluation (leaky column, random rows) looks excellent: {r['leaky_auc']:.3f}."
    assert 0.62 < r["honest_auc"] < 0.80, f"the honest AUC (no leak, no duplicates, group split, encoder inside the pipeline) is about 0.71, got {r['honest_auc']:.3f}."
    assert r["leaky_auc"] - r["honest_auc"] > 0.15, "the audit must show how much of the claim was leakage."


def test_clean_data_has_no_leak_to_report():
    df = make_loans(2000, 200, seed=6, n_vendor=5).drop(columns="collections_calls")
    r = audit(df)
    assert r["leaky_column"] is None, "without the post-outcome column no single feature exceeds 0.9: report None."
