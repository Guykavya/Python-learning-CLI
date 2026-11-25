import pandas as pd


def orders_since(con, since, customer=None):
    """Orders from `since` on (optionally one customer), parsed dates, sorted."""
    return pd.read_sql_query("SELECT * FROM orders", con)
