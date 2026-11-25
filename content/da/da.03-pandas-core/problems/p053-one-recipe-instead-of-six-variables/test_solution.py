import ast
import inspect

import numpy as np
import pandas as pd

import solution
from solution import clean_orders


def clean_orders_script(df):
    t1 = df.copy()
    t1["city"] = t1["city"].str.strip().str.title()
    t2 = t1[t1["qty"] > 0]
    t3 = t2.drop_duplicates(subset="order_id", keep="last")
    t4 = t3.assign(revenue=t3["qty"] * t3["unit_price"] * (1 - t3["discount"].fillna(0)))
    t5 = t4[t4["paid"]]
    t6 = t5.sort_values("revenue", ascending=False)
    t7 = t6.reset_index(drop=True)
    return t7[["order_id", "city", "revenue"]]


def make(n, seed):
    rng = np.random.default_rng(seed)
    cities = np.array(["pune", " Delhi ", "AGRA", "Jaipur  ", "SURAT"])
    return pd.DataFrame({
        "order_id": rng.integers(1, n * 2 // 3, n),
        "city": rng.choice(cities, n),
        "qty": rng.integers(-1, 9, n),
        "unit_price": rng.gamma(4.0, 120.0, n).round(2),
        "discount": rng.choice([0.0, 0.05, 0.1, np.nan], n),
        "paid": rng.random(n) < 0.8,
    })


def test_same_result_as_the_script_on_a_small_table():
    df = pd.DataFrame({
        "order_id": [1, 2, 2, 3, 4],
        "city": [" pune", "DELHI ", "delhi", "agra", "surat"],
        "qty": [2, 1, 3, 0, 5],
        "unit_price": [100.0, 50.0, 50.0, 10.0, 20.0],
        "discount": [0.1, None, 0.5, 0.0, None],
        "paid": [True, True, True, True, False],
    })
    got = clean_orders(df)
    want = clean_orders_script(df)
    pd.testing.assert_frame_equal(got, want, obj="clean_orders(df) versus the script")
    assert got["order_id"].tolist() == [1, 2], f"expected order ids [1, 2] (3 has qty 0, 4 is unpaid, the second row of id 2 wins), got {got['order_id'].tolist()}."
    assert got["city"].tolist() == ["Pune", "Delhi"], f"cities are stripped and title-cased: ['Pune', 'Delhi'], got {got['city'].tolist()}."


def test_same_result_as_the_script_on_random_tables():
    for seed in range(8):
        df = make(300, seed)
        before = df.copy()
        got = clean_orders(df)
        pd.testing.assert_frame_equal(df, before, obj=f"input frame (seed {seed}) - the chain must not change it")
        pd.testing.assert_frame_equal(got, clean_orders_script(df), obj=f"clean_orders versus the script (seed {seed})")


def test_empty_result_is_fine():
    df = make(20, 1).assign(paid=False)
    got = clean_orders(df)
    assert got.shape == (0, 3) and got.columns.tolist() == ["order_id", "city", "revenue"], (
        f"nothing is paid, so the result has no rows but still the three columns; got shape {got.shape}.")


def test_the_body_is_one_return_of_a_chain():
    tree = ast.parse(inspect.getsource(solution))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "clean_orders")
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    assert len(body) == 1 and isinstance(body[0], ast.Return), (
        "the body of clean_orders must be a docstring (optional) and a single `return (...)`: no temporary variables, no extra statements.")
    calls = [n for n in ast.walk(body[0]) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    assert len(calls) >= 6, f"a chain of method calls was expected (the script has seven steps); found only {len(calls)} method calls."
