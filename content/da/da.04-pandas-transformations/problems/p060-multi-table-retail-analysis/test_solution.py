import math
import random

import pandas as pd
import pytest

from solution import analyse

KEYS = {"total_revenue", "by_region_channel", "top_products", "unsold", "never_ordered", "net_revenue",
        "return_rate", "monthly", "ledger", "checks"}


# ---------- the slow, plain-Python version of the project ----------

def slow_project(t):
    order = {r["order_id"]: r for r in t["orders"].to_dict("records")}
    region = dict(zip(t["stores"]["store_id"], t["stores"]["region"]))
    category = dict(zip(t["products"]["product_id"], t["products"]["category"]))
    refund = {(o, p): r for o, p, r in zip(t["returns"]["order_id"], t["returns"]["product_id"], t["returns"]["refund"])}
    total = net = 0.0
    returned = 0
    by_rc, by_prod, by_month = {}, {}, {}
    lines = list(zip(t["items"]["order_id"], t["items"]["product_id"], t["items"]["qty"], t["items"]["unit_price"]))
    for o, p, q, price in lines:
        rev = q * price
        total += rev
        rf = refund.get((o, p))
        if rf is not None:
            returned += 1
        net += rev * (1 - (rf or 0.0))
        od = order[o]
        key = (region[od["store_id"]], od["channel"])
        cell = by_rc.setdefault(key, [0.0, set()])
        cell[0] += rev
        cell[1].add(o)
        by_prod[(category[p], p)] = by_prod.get((category[p], p), 0.0) + rev
        m = "%04d-%02d" % (od["order_date"].year, od["order_date"].month)
        by_month[m] = by_month.get(m, 0.0) + rev
    top = []
    for cat in sorted({c for c, _ in by_prod}):
        ranked = sorted(((p, r) for (c, p), r in by_prod.items() if c == cat), key=lambda pr: (-pr[1], pr[0]))
        top += [[cat, p, r, k] for k, (p, r) in enumerate(ranked[:3], start=1)]
    months = sorted(by_month)
    mom = [float("nan")] + [(by_month[b] / by_month[a] - 1) * 100 for a, b in zip(months, months[1:])]
    return {
        "total_revenue": total,
        "by_region_channel": [[r, c, v[0], len(v[1])] for (r, c), v in sorted(by_rc.items())],
        "top_products": top,
        "unsold": sorted(set(t["products"]["product_id"]) - {p for _, p, _, _ in lines}),
        "never_ordered": sorted(set(t["customers"]["customer_id"]) - set(t["orders"]["customer_id"])),
        "net_revenue": net,
        "return_rate": returned / len(lines),
        "monthly": [[m, by_month[m], x] for m, x in zip(months, mom)],
    }


def random_tables(seed):
    """Six small random tables with the chapter's columns; every month of Jan-Mar 2025 has an order."""
    rng = random.Random(seed)
    customers = pd.DataFrame({"customer_id": ["C%d" % i for i in range(1, 9)],
                              "city": [rng.choice(["Pune", "Delhi", "Agra"]) for _ in range(8)],
                              "segment": [rng.choice(["retail", "premium"]) for _ in range(8)],
                              "signup": pd.to_datetime(["2024-06-01"] * 8)})
    products = pd.DataFrame({"product_id": ["P%02d" % i for i in range(1, 11)],
                             "category": [rng.choice(["grocery", "toys", "home", "office"]) for _ in range(10)],
                             "list_price": [float(rng.randint(40, 900)) for _ in range(10)]})
    stores = pd.DataFrame({"store_id": ["S1", "S2", "S3", "S4"], "store_city": ["Pune", "Delhi", "Agra", "Surat"],
                           "region": ["west", "north", "north", "west"]})
    n = rng.randint(6, 25)
    days = [rng.randint(0, 89) for _ in range(n)]
    days[:3] = [5, 40, 70]                                   # one order in each month for sure
    orders = pd.DataFrame({
        "order_id": range(10001, 10001 + n),
        "customer_id": [rng.choice(["C1", "C2", "C3", "C4", "C5", "C6", "C99"]) for _ in range(n)],
        "store_id": [rng.choice(["S1", "S2", "S3", "S4"]) for _ in range(n)],
        "order_date": pd.Timestamp("2025-01-01") + pd.to_timedelta(days, unit="D"),
        "channel": [rng.choice(["store", "online"]) for _ in range(n)],
    })
    rows = []
    for o in orders["order_id"]:
        for p in rng.sample(["P%02d" % i for i in range(1, 9)], rng.randint(1, 3)):
            rows.append((o, p, rng.randint(1, 5), float(rng.randint(10, 300))))
    items = pd.DataFrame(rows, columns=["order_id", "product_id", "qty", "unit_price"])
    ret = items.sample(n=max(1, len(items) // 6), random_state=seed)[["order_id", "product_id"]]
    returns = ret.assign(reason="damaged", refund=[rng.choice([0.5, 1.0]) for _ in range(len(ret))]).reset_index(drop=True)
    return {"customers": customers, "products": products, "stores": stores, "orders": orders, "items": items,
            "returns": returns}


def compare(got, want, where):
    assert got["total_revenue"] == pytest.approx(want["total_revenue"]), "total revenue (%s)" % where
    rc = got["by_region_channel"]
    assert list(rc.columns) == ["region", "channel", "revenue", "orders"], "by_region_channel columns; got %s" % list(rc.columns)
    g = rc.values.tolist()
    assert [r[:2] + [r[3]] for r in g] == [r[:2] + [r[3]] for r in want["by_region_channel"]], (
        "region/channel rows or DISTINCT order counts differ (%s)" % where)
    assert [r[2] for r in g] == pytest.approx([r[2] for r in want["by_region_channel"]]), "region/channel revenue (%s)" % where
    tp = got["top_products"]
    assert list(tp.columns) == ["category", "product_id", "revenue", "rank"], "top_products columns; got %s" % list(tp.columns)
    g = tp.values.tolist()
    assert [[r[0], r[1], r[3]] for r in g] == [[r[0], r[1], r[3]] for r in want["top_products"]], (
        "top 3 per category (ties by product_id, rank 1..3, sorted by category and rank) differ (%s): %s" % (where, g))
    assert [r[2] for r in g] == pytest.approx([r[2] for r in want["top_products"]])
    assert got["unsold"] == want["unsold"], "unsold products (%s)" % where
    assert got["never_ordered"] == want["never_ordered"], "never-ordered customers (%s)" % where
    assert got["net_revenue"] == pytest.approx(want["net_revenue"]), "net revenue (%s)" % where
    assert got["return_rate"] == pytest.approx(want["return_rate"]), "return rate (%s)" % where
    mo = got["monthly"]
    assert list(mo.columns) == ["month", "revenue", "mom_pct"], "monthly columns; got %s" % list(mo.columns)
    assert mo["month"].tolist() == [r[0] for r in want["monthly"]], "months as 'YYYY-MM' text, sorted (%s)" % where
    assert mo["revenue"].tolist() == pytest.approx([r[1] for r in want["monthly"]]), "monthly revenue (%s)" % where
    assert math.isnan(mo["mom_pct"].iloc[0]), "the first month has no previous month: mom_pct is NaN"
    assert mo["mom_pct"].tolist()[1:] == pytest.approx([r[2] for r in want["monthly"]][1:]), "mom_pct (%s)" % where


# ---------- tests ----------

def test_keys(tables):
    got = analyse(tables)
    assert set(got) == KEYS, "the result dict must have exactly the keys %s; got %s" % (sorted(KEYS), sorted(got))


def test_hand_checked_numbers(tables):
    got = analyse(tables)
    assert got["total_revenue"] == pytest.approx(1670.0), (
        "total revenue = sum of qty * unit_price over all 15 lines = 1670 (the orphan order of C9 counts too)")
    assert got["by_region_channel"]["revenue"].tolist() == pytest.approx([560.0, 665.0, 135.0, 310.0]), (
        "north/online 560, north/store 665, west/online 135, west/store 310")
    assert got["net_revenue"] == pytest.approx(1360.0), "net = 1670 - 120 (P5, refund 1.0) - 100 (half of 200) - 90 = 1360"
    assert got["return_rate"] == pytest.approx(0.2), "3 returned lines of 15 = 0.2"
    assert got["unsold"] == ["P6", "P7"] and got["never_ordered"] == ["C5", "C6"]
    grocery = got["top_products"][got["top_products"]["category"] == "grocery"]["product_id"].tolist()
    assert grocery == ["P4", "P1", "P2"], (
        "grocery: P4 380, P1 345, then P2 and P3 tie at 190: the tie goes to the smaller id (P2); got %s" % grocery)


def test_against_slow_version(tables):
    compare(analyse(tables), slow_project(tables), "chapter-style data")


@pytest.mark.parametrize("seed", range(6))
def test_random_against_slow_version(seed):
    t = random_tables(seed)
    compare(analyse(t), slow_project(t), "seed %d" % seed)


def test_every_merge_kept_its_rows(tables):
    ledger = analyse(tables)["ledger"]
    assert isinstance(ledger, list) and len(ledger) >= 4, (
        "the ledger lists one safe_merge record per join (orders, products, stores, returns at least); got %s" % ledger)
    for r in ledger:
        assert r["result_rows"] == r["left_rows"] == 15, "every merge into the order lines must keep 15 rows: %s" % r
        if "measure_before" in r:
            assert r["measure_before"] == r["measure_after"], "no merge may change the revenue total: %s" % r


def test_duplicated_product_is_refused(tables):
    tables["products"] = pd.concat([tables["products"], tables["products"].iloc[[0]]], ignore_index=True)
    with pytest.raises((pd.errors.MergeError, AssertionError)):
        analyse(tables)


def test_reconciliation_checks(tables):
    checks = analyse(tables)["checks"]
    assert len(checks) >= 3, "reconcile at least three breakdowns against their totals; got %s" % checks
    assert all(ok is True or ok == True for _, ok in checks), "every reconciliation must pass: %s" % checks


def test_missing_month_raises(tables):
    o = tables["orders"]
    tables["orders"] = o.assign(order_date=o["order_date"].where(o["order_date"] >= "2025-02-01",
                                                                 o["order_date"] - pd.Timedelta(days=60)))
    with pytest.raises(ValueError) as err:
        analyse(tables)
    assert "2024-12" in str(err.value), (
        "January orders moved to November: December 2024 has no order, so the month-on-month growth would compare "
        "February with November. Raise ValueError naming the missing month; got %r" % str(err.value))


def test_inputs_unchanged(tables):
    before = {k: v.copy() for k, v in tables.items()}
    analyse(tables)
    for k in tables:
        pd.testing.assert_frame_equal(tables[k], before[k], obj="table " + k)
