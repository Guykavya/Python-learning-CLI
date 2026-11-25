import pandas as pd


def safe_merge(left, right, on, how="left", validate="m:1", measure=None, name="",
               expect_same_rows=True, ledger=None):
    """Merge with validate=, record what happened, stop on a changed row count or measure total (p057)."""
    keys = [on] if isinstance(on, str) else list(on)
    out = left.merge(right, on=on, how=how, validate=validate, indicator=True)
    unmatched = int((out["_merge"] == "left_only").sum())
    out = out.drop(columns="_merge")
    step = name or f"merge on {keys}"
    record = {"step": step, "left_rows": len(left), "right_rows": len(right), "result_rows": len(out),
              "unmatched_left": unmatched}
    if measure is not None:
        record["measure_before"] = round(float(left[measure].sum()), 2)
        record["measure_after"] = round(float(out[measure].sum()), 2)
    if ledger is not None:
        ledger.append(record)
    if how == "left" and expect_same_rows:
        assert len(out) == len(left), f"{step}: row count changed {len(left)} -> {len(out)}"
    if measure is not None:
        assert abs(record["measure_after"] - record["measure_before"]) < 0.01, f"{step}: {measure} total changed"
    return out


def reconcile(parts, total, label="", tol=0.01):
    """(ok, difference) of sum(parts) against total (p058)."""
    diff = round(float(pd.Series(parts).sum()) - total, 2) + 0.0
    return abs(diff) <= tol, diff


def analyse(tables):
    """The chapter 15 project on six tables: a dict of answers, every merge checked, every breakdown reconciled."""
    ledger, checks = [], []

    def check(label, parts, total):
        ok, diff = reconcile(parts, total, label)
        checks.append((label, ok))
        if not ok:
            raise ValueError(f"{label} does not reconcile: diff={diff}")

    base = tables["items"].assign(revenue=lambda d: d["qty"] * d["unit_price"])
    total = float(base["revenue"].sum())
    f = safe_merge(base, tables["orders"], on="order_id", measure="revenue", name="lines + orders", ledger=ledger)
    f = safe_merge(f, tables["products"][["product_id", "category"]], on="product_id", measure="revenue",
                   name="+ products", ledger=ledger)
    f = safe_merge(f, tables["stores"], on="store_id", measure="revenue", name="+ stores", ledger=ledger)
    f = safe_merge(f, tables["returns"][["order_id", "product_id", "refund"]], on=["order_id", "product_id"],
                   validate="1:1", measure="revenue", name="+ returns", ledger=ledger)
    f["returned"] = f["refund"].notna()
    f["refund"] = f["refund"].fillna(0.0)
    f["net_revenue"] = f["revenue"] * (1 - f["refund"])

    # 1. revenue and orders by region and channel
    q1 = (f.groupby(["region", "channel"], as_index=False)
            .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique")))
    check("revenue by region and channel", q1["revenue"], total)
    check("orders by region and channel", q1["orders"], f["order_id"].nunique())

    # 2. top 3 products per category, and the unsold products
    prod = f.groupby(["category", "product_id"], as_index=False)["revenue"].sum()
    prod = prod.sort_values(["category", "revenue", "product_id"], ascending=[True, False, True])
    prod["rank"] = prod.groupby("category").cumcount() + 1
    top = prod[prod["rank"] <= 3].reset_index(drop=True)
    check("revenue by product", prod["revenue"], total)
    products = tables["products"]
    unsold = sorted(products.loc[~products["product_id"].isin(f["product_id"]), "product_id"].tolist())

    # 3. customers who never ordered
    customers = tables["customers"]
    never = sorted(customers.loc[~customers["customer_id"].isin(tables["orders"]["customer_id"]), "customer_id"].tolist())

    # 4. net revenue and return rate
    net = float(f["net_revenue"].sum())
    return_rate = float(f["returned"].mean())
    check("returned lines vs returns table", [int(f["returned"].sum())], len(tables["returns"]))

    # 5. monthly trend on a full calendar
    f["month"] = f["order_date"].dt.to_period("M")
    mt = f.groupby("month")["revenue"].sum()
    full = pd.period_range(mt.index.min(), mt.index.max(), freq="M")
    missing = [str(m) for m in full if m not in mt.index]
    if missing:
        raise ValueError(f"months without any order: {missing}; month-on-month growth would skip them")
    monthly = pd.DataFrame({"month": mt.index.astype(str), "revenue": mt.to_numpy()})
    monthly["mom_pct"] = monthly["revenue"].pct_change() * 100
    check("monthly revenue", monthly["revenue"], total)

    return {
        "total_revenue": total,
        "by_region_channel": q1.sort_values(["region", "channel"]).reset_index(drop=True),
        "top_products": top[["category", "product_id", "revenue", "rank"]],
        "unsold": unsold,
        "never_ordered": never,
        "net_revenue": net,
        "return_rate": return_rate,
        "monthly": monthly,
        "ledger": ledger,
        "checks": checks,
    }
