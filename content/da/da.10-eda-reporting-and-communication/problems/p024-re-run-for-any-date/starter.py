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
    """KPIs of the last complete month before `as_of`, using only data known on `as_of`."""
    raise NotImplementedError
