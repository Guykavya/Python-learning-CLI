"""Shared fixtures for the da.07 SQL problems: one DuckDB connection per test, a row runner, and a small
random LearnLoop data builder. The solution never opens its own connection (DuckDB can crash with three open)."""
import datetime as _dt
import decimal as _dec
import random

import duckdb
import pandas as pd
import pytest


@pytest.fixture
def con():
    with duckdb.connect(config={"threads": 1, "memory_limit": "300MB"}) as c:   # small limits: the runner caps the address space at 1 GiB
        yield c


def _norm(v):
    if isinstance(v, _dt.datetime):
        return v.strftime("%Y-%m-%d") if (v.hour, v.minute, v.second, v.microsecond) == (0, 0, 0, 0) else v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, _dt.date):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, _dec.Decimal):
        return float(v)
    if isinstance(v, pd.Timestamp):
        return _norm(v.to_pydatetime())
    return v


@pytest.fixture
def run(con):
    """run(sql, users=df, events=df, ...) -> (column names, rows). Dates come back as 'YYYY-MM-DD' strings."""
    def _run(sql, **tables):
        for name, df in tables.items():
            con.register(name, df)
        try:
            cur = con.execute(sql)
            cols = [d[0] for d in cur.description]
            rows = [tuple(_norm(v) for v in r) for r in cur.fetchall()]
        except duckdb.Error as e:
            pytest.fail(f"DuckDB rejected your query: {e}")
        return cols, rows
    return _run


def _key(row):
    return tuple("" if v is None else repr(round(v, 6)) if isinstance(v, float) else repr(v) for v in row)


def _eq(a, b):
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a) - float(b)) <= 1e-6 + 1e-6 * abs(float(b))
        except (TypeError, ValueError):
            return False
    return a == b


@pytest.fixture
def same():
    """same(got, want, ordered=False): equal rows (floats to 1e-6, None equals None)."""
    def _same(got, want, ordered=False):
        got, want = [tuple(r) for r in got], [tuple(r) for r in want]
        if len(got) != len(want):
            return False
        if not ordered:
            got, want = sorted(got, key=_key), sorted(want, key=_key)
        return all(len(g) == len(w) and all(_eq(x, y) for x, y in zip(g, w)) for g, w in zip(got, want))
    return _same


def make_data(seed, n_users=30, end="2025-07-15"):
    """A small random LearnLoop: users, events, orders (same columns as the chapter). Deterministic for a seed."""
    rng = random.Random(seed)
    end = pd.Timestamp(end)
    base = pd.Timestamp("2025-01-01")
    urows, erows = [], []
    for uid in range(1, n_users + 1):
        s = base + pd.Timedelta(minutes=rng.randrange(0, 181 * 24 * 60))
        urows.append((uid, s, rng.choice(["organic", "ads", "referral"]), rng.choice(["IN", "US", "UK"])))
        erows.append((uid, s, "login"))
        for _ in range(rng.randrange(0, 12)):
            t = s + pd.Timedelta(minutes=rng.randrange(0, 120 * 24 * 60))
            erows.append((uid, t, "login"))
        if rng.random() < .8:
            t = s + pd.Timedelta(minutes=rng.randrange(1, 3 * 24 * 60))
            for _ in range(rng.randrange(1, 4)):
                erows.append((uid, t, "view_course"))
                t += pd.Timedelta(minutes=rng.randrange(1, 90))
            for step in ["add_to_cart", "checkout_start", "purchase"]:
                if rng.random() < .6:
                    t += pd.Timedelta(minutes=rng.randrange(1, 40 * 60))
                    erows.append((uid, t, step))
                else:
                    break
        elif rng.random() < .2:
            erows.append((uid, s + pd.Timedelta(days=rng.randrange(0, 20)), "purchase"))
    users = pd.DataFrame(urows, columns=["user_id", "signup_at", "channel", "country"])
    events = pd.DataFrame(erows, columns=["user_id", "event_time", "event_type"])
    events = events[events["event_time"] <= end].sort_values(["event_time", "user_id", "event_type"], kind="stable").reset_index(drop=True)
    events.insert(0, "event_id", range(1, len(events) + 1))
    buys = events[events["event_type"] == "purchase"].reset_index(drop=True)
    plans = [rng.choice(["monthly", "annual"]) for _ in range(len(buys))]
    orders = pd.DataFrame({"order_id": [9001 + i for i in range(len(buys))], "user_id": buys["user_id"], "order_time": buys["event_time"],
                           "plan": plans, "amount": [499 if p == "monthly" else 3999 for p in plans]})
    return users, events, orders


@pytest.fixture
def data():
    return make_data
