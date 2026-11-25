import pandas as pd
import pytest
from solution import QUERIES

NAMES = ["monthly_revenue_growth", "retention_grid", "ordered_funnel_by_channel", "top2_spenders_per_country", "active_user_states"]
COLUMNS = {
    "monthly_revenue_growth": ["month", "revenue", "prev_revenue", "growth_pct"],
    "retention_grid": ["cohort", "month_number", "active_users", "cohort_size", "retention"],
    "ordered_funnel_by_channel": ["channel", "viewed", "carted", "checkout", "purchased"],
    "top2_spenders_per_country": ["country", "user_id", "spent", "rank_in_country"],
    "active_user_states": ["month", "mau", "new_users", "retained", "resurrected", "churned"],
}
KEYS = {
    "monthly_revenue_growth": ["month"],
    "retention_grid": ["cohort", "month_number"],
    "ordered_funnel_by_channel": ["channel"],
    "top2_spenders_per_country": ["country", "rank_in_country"],
    "active_user_states": ["month"],
}
STEPS = ["view_course", "add_to_cart", "checkout_start", "purchase"]
CUT = pd.Timestamp("2025-07-01")


def iso(ts):
    return ts.strftime("%Y-%m-%d")


def truth_revenue(users, events, orders):
    o = orders[orders["order_time"] < CUT]
    if o.empty:
        return []
    m = o["order_time"].dt.to_period("M")
    s = o.groupby(m)["amount"].sum().reindex(pd.period_range(m.min(), m.max(), freq="M"), fill_value=0)
    out, prev = [], None
    for p, v in s.items():
        v = int(v)
        out.append((iso(p.start_time), v, prev, None if prev in (None, 0) else (v - prev) * 100.0 / prev))
        prev = v
    return out


def truth_retention(users, events, orders):
    u = users.assign(cohort=users["signup_at"].dt.to_period("M"))
    size = u.groupby("cohort").size()
    login = events[(events["event_type"] == "login") & (events["event_time"] < CUT)]
    am = login.assign(m=login["event_time"].dt.to_period("M"))[["user_id", "m"]].drop_duplicates()
    j = am.merge(u[["user_id", "cohort"]], on="user_id")
    j["k"] = (j["m"] - j["cohort"]).apply(lambda x: x.n)
    act = j.groupby(["cohort", "k"])["user_id"].nunique()
    out = []
    for c in size.index:
        for k in range(6):
            obs = (c + k).start_time < CUT
            a = int(act.get((c, k), 0)) if obs else None
            out.append((iso(c.start_time), k, a, int(size[c]), (a / size[c]) if obs else None))
    return out


def truth_funnel(users, events, orders):
    out = {}
    for r in users.itertuples():
        e = events[events["user_id"] == r.user_id]
        t = [e.loc[e["event_type"] == s, "event_time"].min() for s in STEPS]
        row = out.setdefault(r.channel, [0, 0, 0, 0])
        if pd.notna(t[0]):
            row[0] += 1
            if pd.notna(t[1]) and t[1] >= t[0]:
                row[1] += 1
                if pd.notna(t[2]) and t[2] >= t[1]:
                    row[2] += 1
                    if pd.notna(t[3]) and t[3] >= t[2]:
                        row[3] += 1
    return [(ch, *v) for ch, v in out.items()]


def truth_top2(users, events, orders):
    m = orders.merge(users[["user_id", "country"]], on="user_id")
    s = m.groupby(["country", "user_id"], as_index=False)["amount"].sum().rename(columns={"amount": "spent"})
    s = s.sort_values(["country", "spent", "user_id"], ascending=[True, False, True])
    out = []
    for c, g in s.groupby("country"):
        for i, r in enumerate(g.head(2).itertuples(), start=1):
            out.append((c, int(r.user_id), int(r.spent), i))
    return out


def truth_states(users, events, orders):
    login = events[(events["event_type"] == "login") & (events["event_time"] < CUT)]
    am = login.assign(m=login["event_time"].dt.to_period("M"))[["user_id", "m"]].drop_duplicates()
    by = {}
    for _uid, g in am.groupby("user_id"):
        ms = sorted(g["m"])
        for i, m in enumerate(ms):
            st = by.setdefault(m, [0, 0, 0, 0])
            st[0] += 1
            if i == 0:
                st[1] += 1
            elif ms[i - 1] == m - 1:
                st[2] += 1
            else:
                st[3] += 1
    out, prev = [], None
    for m in sorted(by):
        mau, new, ret, res = by[m]
        out.append((iso(m.start_time), mau, new, ret, res, None if prev is None else prev - ret))
        prev = mau
    return out


TRUTH = {"monthly_revenue_growth": truth_revenue, "retention_grid": truth_retention, "ordered_funnel_by_channel": truth_funnel,
         "top2_spenders_per_country": truth_top2, "active_user_states": truth_states}


def test_five_named_queries():
    assert sorted(QUERIES) == sorted(NAMES), f"QUERIES must have exactly these keys: {NAMES}."


@pytest.mark.parametrize("name", NAMES)
def test_definition_comment(name):
    assert QUERIES[name].lstrip().startswith("--"), f"{name}: start the query with a -- comment that states its definition and grain."


@pytest.mark.parametrize("name", NAMES)
def test_columns(run, data, name):
    u, e, o = data(62, 50)
    cols, _ = run(QUERIES[name], users=u, events=e, orders=o)
    assert cols == COLUMNS[name], f"{name}: columns must be {COLUMNS[name]}."


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("seed", [63, 64])
def test_matches_pandas_truth(run, same, data, name, seed):
    u, e, o = data(seed, 60)
    cols, rows = run(QUERIES[name], users=u, events=e, orders=o)
    want = TRUTH[name](u, e, o)
    assert same(rows, want), f"{name}: result differs from the independent pandas computation (see the definition in the problem statement)."


@pytest.mark.parametrize("name", NAMES)
def test_grain(run, data, name):
    u, e, o = data(65, 60)
    cols, rows = run(QUERIES[name], users=u, events=e, orders=o)
    idx = [cols.index(k) for k in KEYS[name]]
    keys = [tuple(r[i] for i in idx) for r in rows]
    assert len(keys) == len(set(keys)), f"{name}: the grain is wrong, the key {KEYS[name]} has duplicates ({len(keys)} rows, {len(set(keys))} distinct keys)."
    assert not any(None in k for k in keys), f"{name}: NULL in the key {KEYS[name]}."


def test_retention_cells_after_the_cutoff_are_null(run, data):
    u, e, o = data(66, 60)
    cols, rows = run(QUERIES["retention_grid"], users=u, events=e, orders=o)
    for cohort, k, active, size, ret in rows:
        if pd.Timestamp(cohort) + pd.DateOffset(months=k) >= CUT:
            assert active is None and ret is None, f"Cell ({cohort}, {k}) is not observed yet: it must be NULL, not {active}."
