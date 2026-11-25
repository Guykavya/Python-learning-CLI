from dataclasses import dataclass
from typing import Callable

import pandas as pd
import pytest

from solution import metrics_table


@dataclass(frozen=True)
class MetricSpec:
    name: str
    unit: str
    fn: Callable


# jobs (job_id, status, created_at, completed_at, quote_total): every row has a reason
JOBS = [
    (1, "completed", "2025-01-10 09:00:00", "2025-01-12 10:00:00", 1000),   # plain January job
    (2, "completed", "2025-01-31 23:59:59", "2025-02-01 00:00:00", 2000),   # created last second of Jan, completed exactly at the start of Feb
    (3, "cancelled", "2025-02-01 00:00:00", None, 500),                     # created exactly at the start of Feb
    (4, "completed", "2025-02-05 09:00:00", "2025-02-06 09:00:00", 1500),   # plain February job
    (5, "pending", "2025-02-20 09:00:00", None, 800),                       # pending: out of the completion-rate denominator
    (6, "completed", "2025-02-28 23:59:59", "2025-03-01 00:00:00", 3000),   # completed exactly at the start of March
    (7, "failed", "2025-03-02 09:00:00", None, 400),                        # failed: in the denominator, not the numerator
    (8, "completed", "2025-03-10 09:00:00", "2025-03-11 09:00:00", 2500),   # plain March job
    (9, "pending", "2025-03-15 09:00:00", None, 600),                       # pending
    (10, "completed", "2025-04-01 00:00:00", "2025-04-02 09:00:00", 900),   # April: in no month of the table
]
PAYMENTS = [(1, 1, "2025-01-12 12:00:00", 1000), (2, 2, "2025-02-01 00:00:00", 800), (3, 2, "2025-02-10 09:00:00", 1200),
            (4, 4, "2025-02-06 12:00:00", 1500), (5, 6, "2025-03-01 00:00:00", 3000), (6, 8, "2025-03-31 23:59:59", 2500),
            (7, 10, "2025-04-01 00:00:00", 900)]
MONTHS = {"Jan": ("2025-01-01", "2025-02-01"), "Feb": ("2025-02-01", "2025-03-01"), "Mar": ("2025-03-01", "2025-04-01")}


def make_ctx():
    j = pd.DataFrame(JOBS, columns=["job_id", "status", "created_at", "completed_at", "quote_total"])
    j["created_at"] = pd.to_datetime(j["created_at"])
    j["completed_at"] = pd.to_datetime(j["completed_at"])
    p = pd.DataFrame(PAYMENTS, columns=["payment_id", "job_id", "paid_at", "amount"])
    p["paid_at"] = pd.to_datetime(p["paid_at"])
    return {"jobs": j, "pay": p}


def inside(s, start, end):
    return (s >= start) & (s < end)


def f_created(c, s, e):
    n = int(inside(c["jobs"]["created_at"], s, e).sum())
    return n, n, None


def f_completed(c, s, e):
    j = c["jobs"]
    n = int((inside(j["completed_at"], s, e) & j["status"].eq("completed")).sum())
    return n, n, None


def f_rate(c, s, e):
    j = c["jobs"]
    cohort = j[inside(j["created_at"], s, e) & ~j["status"].eq("pending")]
    top, bottom = int(cohort["status"].eq("completed").sum()), len(cohort)
    return top / bottom, top, bottom


def f_cash(c, s, e):
    v = int(c["pay"].loc[inside(c["pay"]["paid_at"], s, e), "amount"].sum())
    return v, v, None


def f_ticket(c, s, e):
    j = c["jobs"]
    m = inside(j["completed_at"], s, e) & j["status"].eq("completed")
    return float(j.loc[m, "quote_total"].mean()), int(j.loc[m, "quote_total"].sum()), int(m.sum())


SPECS = [MetricSpec("jobs_created", "jobs", f_created), MetricSpec("jobs_completed", "jobs", f_completed),
         MetricSpec("completion_rate", "share of jobs", f_rate), MetricSpec("cash_collected", "rupees", f_cash),
         MetricSpec("avg_ticket", "rupees per job", f_ticket)]


def slow_truth():
    """Every cell by a plain loop over the rows, without pandas masks. {(metric, month): (value, numerator, denominator)}"""
    out = {}
    for label, (s, e) in MONTHS.items():
        s, e = pd.Timestamp(s), pd.Timestamp(e)
        created = completed = cohort_done = cohort_all = tick_sum = tick_n = cash = 0
        for (jid, status, c_at, d_at, q) in JOBS:
            c_at = pd.Timestamp(c_at)
            d_at = pd.Timestamp(d_at) if d_at else None
            if s <= c_at < e:
                created += 1
                if status != "pending":
                    cohort_all += 1
                    cohort_done += status == "completed"
            if status == "completed" and d_at is not None and s <= d_at < e:
                completed += 1
                tick_sum += q
                tick_n += 1
        for (_, _, p_at, amount) in PAYMENTS:
            if s <= pd.Timestamp(p_at) < e:
                cash += amount
        out[("jobs_created", label)] = (created, created, None)
        out[("jobs_completed", label)] = (completed, completed, None)
        out[("completion_rate", label)] = (cohort_done / cohort_all, cohort_done, cohort_all)
        out[("cash_collected", label)] = (cash, cash, None)
        out[("avg_ticket", label)] = (tick_sum / tick_n, tick_sum, tick_n)
    return out


def test_shape_columns_and_order():
    t = metrics_table(make_ctx(), SPECS, MONTHS)
    assert list(t.columns) == ["metric", "month", "unit", "numerator", "denominator", "value"], "columns: metric, month, unit, numerator, denominator, value. Got %s." % list(t.columns)
    assert len(t) == 15, "5 metrics x 3 months = 15 rows. Got %d." % len(t)
    want = [(m.name, mo) for m in SPECS for mo in MONTHS]
    assert list(zip(t["metric"], t["month"])) == want, "order: metrics in the order of specs, months in the order of the dict. Got %s." % list(zip(t["metric"], t["month"]))
    assert list(t.index) == list(range(15)), "use the index 0, 1, 2, ..."
    assert t["unit"].tolist()[:3] == ["jobs"] * 3 and t["unit"].tolist()[6:9] == ["share of jobs"] * 3, "unit comes from the spec."


def test_hand_counted_anchor_cells():
    t = metrics_table(make_ctx(), SPECS, MONTHS).set_index(["metric", "month"])
    assert t.loc[("jobs_created", "Feb"), "value"] == 4, "February created: jobs 3 (exactly at the start), 4, 5, 6 = 4."
    assert t.loc[("jobs_completed", "Feb"), "value"] == 2, "completed in February: job 2 (exactly at the start) and job 4; job 6 completes exactly at the end of Feb (= March)."
    assert t.loc[("jobs_completed", "Mar"), "value"] == 2, "March: jobs 6 (at the start) and 8."
    assert (t.loc[("completion_rate", "Feb"), "numerator"], t.loc[("completion_rate", "Feb"), "denominator"]) == (2, 3), (
        "February cohort: jobs 3, 4, 5, 6; pending job 5 is not in the denominator: 2 completed of 3.")
    assert t.loc[("completion_rate", "Mar"), "value"] == pytest.approx(0.5), "March cohort: 7 (failed), 8 (completed), 9 (pending): 1 of 2."
    assert t.loc[("cash_collected", "Feb"), "value"] == 3500, "February cash: 800 (exactly at the start) + 1200 + 1500 = 3,500."
    assert t.loc[("avg_ticket", "Feb"), "value"] == pytest.approx(1750), "(2000 + 1500) / 2."


def test_every_cell_equals_the_slow_loop():
    t = metrics_table(make_ctx(), SPECS, MONTHS)
    truth = slow_truth()
    for r in t.itertuples():
        value, num, den = truth[(r.metric, r.month)]
        assert r.value == pytest.approx(value), "value of %s in %s: expected %s, got %s." % (r.metric, r.month, value, r.value)
        assert r.numerator == num, "numerator of %s in %s: expected %s, got %s." % (r.metric, r.month, num, r.numerator)
        if den is None:
            assert pd.isna(r.denominator), "%s is a count: its denominator cell must be missing (NaN), not %r." % (r.metric, r.denominator)
        else:
            assert r.denominator == den, "denominator of %s in %s: expected %s, got %s." % (r.metric, r.month, den, r.denominator)


def test_fn_gets_timestamps_and_ctx_is_untouched():
    seen = []

    def spy(ctx, start, end):
        seen.append((type(start), type(end), start, end))
        return 1, 1, None

    ctx = make_ctx()
    metrics_table(ctx, [MetricSpec("spy", "x", spy)], {"Feb": ("2025-02-01", "2025-03-01")})
    assert seen == [(pd.Timestamp, pd.Timestamp, pd.Timestamp("2025-02-01"), pd.Timestamp("2025-03-01"))], (
        "call fn(ctx, pd.Timestamp(start), pd.Timestamp(end)) exactly once per metric and month. Got %s." % seen)
    pd.testing.assert_frame_equal(ctx["jobs"], make_ctx()["jobs"])


def test_one_metric_defined_once_works_for_any_months():
    t = metrics_table(make_ctx(), SPECS[:1], {"Apr": ("2025-04-01", "2025-05-01"), "Jan": ("2025-01-01", "2025-02-01")})
    assert t["month"].tolist() == ["Apr", "Jan"] and t["value"].tolist() == [1, 2], "the same code serves any months, in the order given. Got %s." % t.to_dict("records")
