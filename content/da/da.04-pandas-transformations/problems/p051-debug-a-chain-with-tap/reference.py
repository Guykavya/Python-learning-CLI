import pandas as pd


def tap(d, label, log):
    """Append (label, d.shape) to log and return d unchanged."""
    log.append((label, d.shape))
    return d


def clean_items(items, log):
    """One chain: start -> valid qty -> no duplicates -> with revenue -> per order, tapping after each step."""
    return (
        items
        .pipe(tap, "start", log)
        .loc[lambda d: d["qty"].notna() & (d["qty"] > 0)]
        .pipe(tap, "valid qty", log)
        .drop_duplicates()
        .pipe(tap, "no duplicates", log)
        .assign(revenue=lambda d: d["qty"] * d["unit_price"])
        .pipe(tap, "with revenue", log)
        .groupby("order_id", as_index=False)["revenue"].sum()
        .pipe(tap, "per order", log)
        .reset_index(drop=True)
    )
