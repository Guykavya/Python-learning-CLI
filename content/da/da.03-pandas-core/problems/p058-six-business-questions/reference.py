import pandas as pd


def _sales(df):
    return df[~df["returned"]]


def revenue_by_month(df):
    revenue = (df["qty"] * df["unit_price"]).where(~df["returned"], 0.0)
    monthly = revenue.set_axis(df["order_date"]).resample("MS").sum()
    monthly.index = monthly.index.strftime("%Y-%m")
    return monthly.astype(float)


def top_products(df, n=5):
    counts = _sales(df)["product"].value_counts()
    pairs = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(p, int(c)) for p, c in pairs[:n]]


def channel_share(df):
    shares = _sales(df)["channel"].value_counts(normalize=True)
    return {k: float(v) for k, v in shares.items()}


def average_order_value(df):
    sales = _sales(df)
    return float((sales["qty"] * sales["unit_price"]).sum() / len(sales))


def repeat_customer_share(df):
    orders_per_customer = _sales(df)["customer"].value_counts()
    return float((orders_per_customer >= 2).mean())


def returns_rate(df):
    return float(df["returned"].mean())
