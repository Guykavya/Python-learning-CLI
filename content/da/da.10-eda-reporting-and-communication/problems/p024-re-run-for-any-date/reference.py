import pandas as pd


def monthly_kpis(customers, panel):
    """The KPI table of section 3.4 (given)."""
    p = panel.assign(month=panel["week"].dt.to_period("M"))
    first = p.groupby("month")["week"].min()
    opening = p[p["week"].isin(first.values)][["customer_id", "month"]]
    opening = opening.merge(customers[["customer_id", "last_week"]], on="customer_id", how="left", validate="m:1")
    opening["churned"] = opening["last_week"].dt.to_period("M") == opening["month"]
    out = opening.groupby("month").agg(opening_actives=("customer_id", "size"), churned=("churned", "sum"))
    out["churn_rate_pct"] = out["churned"] / out["opening_actives"] * 100
    out["on_time_pct"] = (1 - p.groupby("month")["late"].mean()) * 100
    return out


def quick_summary(customers, panel, as_of):
    as_of = pd.Timestamp(as_of)
    pnl = panel[panel["week"] <= as_of]
    cus = customers.assign(last_week=customers["last_week"].where(customers["last_week"] <= as_of))
    last_month = as_of.to_period("M") - 1
    k = monthly_kpis(cus, pnl[pnl["week"].dt.to_period("M") <= last_month])
    row = k.iloc[-1]
    return {"as_of": str(as_of.date()), "last_month": str(k.index[-1]), "months": int(len(k)),
            "opening_last": int(row["opening_actives"]), "churn_last": float(row["churn_rate_pct"]),
            "on_time_last": float(row["on_time_pct"])}
