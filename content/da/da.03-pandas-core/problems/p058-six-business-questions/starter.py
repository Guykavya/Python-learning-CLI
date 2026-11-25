import pandas as pd


def revenue_by_month(df):
    """Series indexed by 'YYYY-MM', every month from first to last order, revenue of non-returned orders."""
    # TODO: revenue column (0 for returned rows), set the dates as index, resample("MS").sum()
    raise NotImplementedError


def top_products(df, n=5):
    """[(product, orders), ...] for the n products with most non-returned orders."""
    raise NotImplementedError


def channel_share(df):
    """{channel: share of non-returned orders}."""
    raise NotImplementedError


def average_order_value(df):
    """Revenue of non-returned orders / number of non-returned orders."""
    raise NotImplementedError


def repeat_customer_share(df):
    """Share of customers (with a non-returned order) that have two or more."""
    raise NotImplementedError


def returns_rate(df):
    """Share of all orders that were returned."""
    raise NotImplementedError
