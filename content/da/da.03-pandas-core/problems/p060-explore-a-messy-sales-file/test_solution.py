import csv
import re
from datetime import datetime

import pandas as pd
import pytest

from solution import explore

COLUMNS = ["order_id", "order_date", "customer", "city", "product", "category", "qty", "unit_price", "discount",
           "paid", "flag_date", "flag_qty", "flag_price", "flag_id", "usable", "revenue"]
START, END = datetime(2025, 1, 1), datetime(2025, 6, 30)
FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y")


# ---------- the slow, plain-Python version of the whole project ----------

def money(t):
    if t is None or t == "":
        return None
    t = re.sub(r"(?i)rs\.?|₹|inr", "", t).replace(",", "").strip()
    try:
        return float(t)
    except ValueError:
        return None


def percent(t):
    if t is None or t == "":
        return None
    try:
        v = float(t.replace("%", "").strip())
    except ValueError:
        return None
    return v / 100 if v > 1 else v


def when(t):
    if t is None or t == "":
        return None
    for f in FORMATS:
        try:
            return datetime.strptime(t.strip(), f)
        except ValueError:
            pass
    return None


def whole(t):
    if t is None or t in ("", "N/A"):
        return None
    try:
        v = float(t)
    except ValueError:
        return None
    return int(v) if v == int(v) else None


def truth(t):
    if t is None or t == "":
        return None
    t = t.strip().lower()
    return True if t in ("yes", "y", "true", "1") else (False if t in ("no", "n", "false", "0") else None)


def slow_project(path):
    with open(path, encoding="utf-8", newline="") as fh:
        raw_rows = list(csv.DictReader(fh))
    seen, rows, removed = set(), [], 0
    for r in raw_rows:
        key = tuple(r.values())
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        rows.append({
            "order_id": r["order_id"], "date": when(r["order_date"]), "qty": whole(r["qty"]),
            "price": money(r["unit_price"]), "disc": percent(r["discount"]), "paid": truth(r["paid"]),
        })
    ids = {}
    for r in rows:
        ids[r["order_id"]] = ids.get(r["order_id"], 0) + 1
    for r in rows:
        r["flag_date"] = r["date"] is None or not (START <= r["date"] <= END)
        r["flag_qty"] = r["qty"] is None or not (1 <= r["qty"] <= 50)
        r["flag_price"] = r["price"] is None or not (10 <= r["price"] <= 20000)
        r["flag_id"] = ids[r["order_id"]] > 1
        r["usable"] = not (r["flag_date"] or r["flag_qty"] or r["flag_price"] or r["flag_id"])
        r["revenue"] = (r["qty"] * r["price"] * (1 - (r["disc"] or 0.0))) if r["qty"] is not None and r["price"] is not None else None
    return rows, removed


def slow_answers(rows):
    ok = [r for r in rows if r["usable"]]
    total = sum(r["revenue"] for r in ok)
    months = {}
    days = {}
    for r in ok:
        key = r["date"].strftime("%Y-%m")
        months[key] = months.get(key, 0.0) + r["revenue"]
        day = r["date"].strftime("%A")
        days[day] = days.get(day, 0) + 1
    best = min(months, key=lambda m: (-months[m], m))
    top5 = [r["order_id"] for r in sorted(ok, key=lambda r: (-r["revenue"], r["order_id"]))[:5]]
    busiest = sorted(days.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    paid = sum(r["revenue"] for r in ok if r["paid"] is True)
    gross = sum(r["qty"] * r["price"] for r in ok)
    return {
        "revenue": total, "best_month": best, "top5": top5, "busiest_weekday": busiest,
        "unpaid_share": (total - paid) / total, "discount_cost_share": (gross - total) / gross,
    }


@pytest.fixture(scope="module")
def run(messy_csv, tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("results") / "out"          # does not exist yet
    answers = explore(messy_csv, out_dir)
    rows, removed = slow_project(messy_csv)
    return answers, out_dir, rows, removed


# ---------- tests ----------

def test_the_two_files_are_written(run):
    _, out_dir, _, _ = run
    assert (out_dir / "clean.parquet").is_file(), "explore must create out_dir if needed and write out_dir / 'clean.parquet'."
    assert (out_dir / "problems.csv").is_file(), "explore must write out_dir / 'problems.csv'."


def test_clean_parquet_columns_and_rows(run):
    _, out_dir, rows, _ = run
    clean = pd.read_parquet(out_dir / "clean.parquet")
    assert clean.columns.tolist() == COLUMNS, f"clean.parquet columns should be {COLUMNS}, got {clean.columns.tolist()}."
    assert len(clean) == len(rows), f"exact duplicate rows must be dropped (and nothing else): expected {len(rows)} rows, got {len(clean)}."
    assert clean["order_id"].tolist() == [r["order_id"] for r in rows], "rows keep the order of the file (after removing the duplicates); order_id stays text."


def test_clean_parquet_values(run):
    _, out_dir, rows, _ = run
    clean = pd.read_parquet(out_dir / "clean.parquet")
    for col, key in (("qty", "qty"), ("unit_price", "price"), ("paid", "paid")):
        got = [None if pd.isna(v) else v for v in clean[col].tolist()]
        want = [r[key] for r in rows]
        assert [None if g is None else float(g) for g in got] == [None if w is None else float(w) for w in want], (
            f"column {col!r} differs from the plain-Python conversion (see chapter 18.2 for the rules).")
    dates = [None if pd.isna(v) else v.to_pydatetime() for v in clean["order_date"]]
    assert dates == [r["date"] for r in rows], "order_date must be parsed with the three formats in order (an impossible date is NaT)."
    got_disc = [None if pd.isna(v) else float(v) for v in clean["discount"]]
    assert got_disc == pytest.approx([r["disc"] for r in rows], nan_ok=True) or got_disc == [r["disc"] for r in rows], "discount: '5%' is 0.05, '0.15' stays 0.15, missing stays missing."


def test_flags_and_usable_and_revenue(run):
    _, out_dir, rows, _ = run
    clean = pd.read_parquet(out_dir / "clean.parquet")
    for flag in ("flag_date", "flag_qty", "flag_price", "flag_id", "usable"):
        got = [bool(v) for v in clean[flag]]
        want = [r[flag] for r in rows]
        assert not clean[flag].isna().any(), f"{flag} must hold True/False only (a missing value is a flagged problem, not an unknown)."
        assert got == want, f"{flag} differs in {sum(g != w for g, w in zip(got, want))} rows. " + {
            "flag_date": "date outside 2025-01-01 .. 2025-06-30, or missing.",
            "flag_qty": "qty missing, below 1 or above 50. Remember that between() on a nullable column returns <NA> for a missing value: fillna(False) before negating.",
            "flag_price": "unit_price missing, below 10 or above 20,000 (same <NA> trap).",
            "flag_id": "order_id appears more than once after the exact duplicates are gone (keep=False marks all of them).",
            "usable": "usable = none of the four flags.",
        }[flag]
    rev = [None if pd.isna(v) else float(v) for v in clean["revenue"]]
    for g, r in zip(rev, rows):
        if r["revenue"] is None:
            assert g is None, "revenue must be missing when qty or unit_price is missing."
        else:
            assert g == pytest.approx(r["revenue"]), "revenue = qty * unit_price * (1 - discount), a missing discount counting as 0."


def test_problem_register_file(run):
    _, out_dir, rows, removed = run
    reg = pd.read_csv(out_dir / "problems.csv")
    assert reg.columns.tolist() == ["problem", "rows"], f"problems.csv has the columns problem and rows, got {reg.columns.tolist()}."
    got = dict(zip(reg["problem"], reg["rows"]))
    want = {
        "exact_duplicates_removed": removed,
        "flag_date": sum(r["flag_date"] for r in rows),
        "flag_qty": sum(r["flag_qty"] for r in rows),
        "flag_price": sum(r["flag_price"] for r in rows),
        "flag_id": sum(r["flag_id"] for r in rows),
        "any_flag": sum(not r["usable"] for r in rows),
    }
    assert list(reg["problem"]) == list(want), f"the register lists {list(want)} in this order, got {list(reg['problem'])}."
    assert got == want, f"register counts should be {want}, got {got}."


def test_the_six_answers(run):
    answers, _, rows, _ = run
    want = slow_answers(rows)
    assert isinstance(answers, dict) and set(answers) == set(want), f"explore returns a dict with the keys {sorted(want)}, got {sorted(answers) if isinstance(answers, dict) else type(answers).__name__}."
    assert answers["revenue"] == pytest.approx(want["revenue"]), f"revenue of the usable orders should be {want['revenue']:.2f}, got {answers['revenue']}."
    assert answers["best_month"] == want["best_month"], f"best month should be {want['best_month']!r}, got {answers['best_month']!r}."
    assert answers["top5"] == want["top5"], f"the five biggest usable orders (order_id as text, largest first): {want['top5']}, got {answers['top5']}."
    assert answers["busiest_weekday"] == want["busiest_weekday"], f"busiest weekday should be {want['busiest_weekday']!r}, got {answers['busiest_weekday']!r}."
    assert answers["unpaid_share"] == pytest.approx(want["unpaid_share"]), (
        f"unpaid_share = (revenue of usable orders that are not paid=True, including unknown) / total revenue = {want['unpaid_share']:.4f}, got {answers['unpaid_share']}.")
    assert answers["discount_cost_share"] == pytest.approx(want["discount_cost_share"]), (
        f"discount_cost_share = (gross - revenue) / gross on usable orders = {want['discount_cost_share']:.4f}, got {answers['discount_cost_share']}.")


def test_answers_are_plain_python_values(run):
    answers, _, _, _ = run
    assert isinstance(answers["revenue"], float) and isinstance(answers["unpaid_share"], float) and isinstance(answers["discount_cost_share"], float), "the numbers must be plain floats."
    assert isinstance(answers["top5"], list) and all(isinstance(x, str) for x in answers["top5"]), "top5 is a list of order ids as text."
    assert isinstance(answers["best_month"], str) and re.fullmatch(r"\d{4}-\d{2}", answers["best_month"]), "best_month looks like '2025-03'."


def test_explore_can_run_twice_into_the_same_folder(messy_csv, tmp_path):
    first = explore(messy_csv, tmp_path)
    second = explore(messy_csv, tmp_path)
    assert first == second, "running explore twice into the same folder must give the same answers (overwrite the files, do not fail)."
