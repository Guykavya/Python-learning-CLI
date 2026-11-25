import numpy as np
import pandas as pd
import streamlit as st

CHURN_NOTE = ("Monthly churn = share of the customers active in the first week of the month "
              "whose last active week falls in the month.")


def filter_data(customers, panel, channels, plans, cities):
    """(customers, panel) for the chosen segments, or None for an empty selection or no panel rows."""
    raise NotImplementedError


def monthly_kpis(customers, panel):
    """Per month: opening_actives, churned, churn_rate_pct, on_time_pct (section 3.4)."""
    raise NotImplementedError


def baseline(kpis, start="2024-04", end="2024-08"):
    """{'churn': mean churn_rate_pct, 'on_time': mean on_time_pct} over the baseline months."""
    raise NotImplementedError


def finding_text(kpis, base):
    """One sentence for the Findings tab (exact format in the statement)."""
    raise NotImplementedError


def main(customers, panel):
    """The app: title, caption, sidebar filters, warning on empty selection, Findings and Explore tabs."""
    raise NotImplementedError


def demo_data(seed=0, n=300):
    """A small random data set so that `streamlit run solution.py` shows something (not the course data)."""
    rng = np.random.default_rng(seed)
    weeks = pd.date_range("2024-01-01", "2024-12-30", freq="W-MON")
    customers = pd.DataFrame({"customer_id": np.arange(n), "channel": rng.choice(["paid", "organic", "referral"], n),
                              "plan": rng.choice(["2-meal", "3-meal"], n), "city": rng.choice(["Metro", "Large", "Small"], n)})
    last = rng.integers(5, len(weeks) + 20, n)
    customers["last_week"] = [weeks[i] if i < len(weeks) else pd.NaT for i in last]
    rows = [{"customer_id": c, "week": weeks[w], "late": bool(rng.random() < 0.1), "price": 599}
            for c in range(n) for w in range(min(last[c] + 1, len(weeks)))]
    return customers, pd.DataFrame(rows)


if __name__ == "__main__":
    main(*demo_data())
