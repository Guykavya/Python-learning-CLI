## Approach

Four small functions carry all the numbers and are tested without Streamlit. `main` only wires widgets to them. The empty selection is handled once, before any number is computed, so no tile can show a misleading value.

## Code

```python
import numpy as np
import pandas as pd
import streamlit as st

CHURN_NOTE = ("Monthly churn = share of the customers active in the first week of the month "
              "whose last active week falls in the month.")


def filter_data(customers, panel, channels, plans, cities):
    if not channels or not plans or not cities:
        return None
    cus = customers[customers["channel"].isin(channels) & customers["plan"].isin(plans) & customers["city"].isin(cities)]
    pan = panel[panel["customer_id"].isin(cus["customer_id"])]
    return (cus, pan) if len(pan) else None


def monthly_kpis(customers, panel):
    p = panel.assign(month=panel["week"].dt.to_period("M"))
    first = p.groupby("month")["week"].min()
    opening = p[p["week"].isin(first.values)][["customer_id", "month"]]
    opening = opening.merge(customers[["customer_id", "last_week"]], on="customer_id", how="left", validate="m:1")
    opening["churned"] = opening["last_week"].dt.to_period("M") == opening["month"]
    out = opening.groupby("month").agg(opening_actives=("customer_id", "size"), churned=("churned", "sum"))
    out["churn_rate_pct"] = out["churned"] / out["opening_actives"] * 100
    out["on_time_pct"] = (1 - p.groupby("month")["late"].mean()) * 100
    return out


def baseline(kpis, start="2024-04", end="2024-08"):
    b = kpis.loc[start:end]
    return {"churn": float(b["churn_rate_pct"].mean()), "on_time": float(b["on_time_pct"].mean())}


def finding_text(kpis, base):
    last = kpis.iloc[-1]
    c, o = float(last["churn_rate_pct"]), float(last["on_time_pct"])
    return (f"In {kpis.index[-1]}, monthly churn was {c:.1f}% against {base['churn']:.1f}% in the baseline period "
            f"({c - base['churn']:+.1f} points); {o:.0f}% of boxes arrived on time against {base['on_time']:.0f}%.")


def main(customers, panel):
    st.title("FreshBox: churn dashboard")
    st.caption(CHURN_NOTE)
    with st.sidebar:
        st.header("Filters")
        options = {c: sorted(customers[c].unique()) for c in ("channel", "plan", "city")}
        channels = st.multiselect("Channel", options["channel"], default=options["channel"])
        plans = st.multiselect("Plan", options["plan"], default=options["plan"])
        cities = st.multiselect("City", options["city"], default=options["city"])
    sel = filter_data(customers, panel, channels, plans, cities)
    if sel is None:
        st.warning("Select at least one value in every filter.")
        return
    kpis = monthly_kpis(*sel)
    base = baseline(kpis)
    last = kpis.index[-1]
    tab_find, tab_explore = st.tabs(["Findings", "Explore"])
    with tab_find:
        st.markdown(finding_text(kpis, base))
    with tab_explore:
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Opening actives, {last}", f"{int(kpis['opening_actives'].iloc[-1]):,}")
        c2.metric(f"Monthly churn, {last}", f"{kpis['churn_rate_pct'].iloc[-1]:.1f}%",
                  delta=f"{kpis['churn_rate_pct'].iloc[-1] - base['churn']:+.1f} points vs baseline", delta_color="inverse")
        c3.metric(f"Boxes on time, {last}", f"{kpis['on_time_pct'].iloc[-1]:.0f}%",
                  delta=f"{kpis['on_time_pct'].iloc[-1] - base['on_time']:+.0f} points vs baseline")
        chart = kpis[["churn_rate_pct"]].copy()
        chart.index = chart.index.to_timestamp()
        st.line_chart(chart)

```

## Complexity

O(n log n) per rerun for the KPI table. For a big data set, cache the loading and the KPI step with `@st.cache_data` keyed by the filter tuples (problem 29, chapter section 9.3).

## Another way

Put the logic in its own module (`fb_metrics.py`, as in the chapter) and import it in `app.py`. One file is used here only because the course copies a single `solution.py`.
