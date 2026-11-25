import pandas as pd


def orders_since(con, since, customer=None):
    """Orders from `since` on (optionally one customer), parsed dates, sorted."""
    sql = "SELECT order_id, customer, order_date, qty FROM orders WHERE order_date >= ?"
    params = [since]
    if customer is not None:
        sql += " AND customer = ?"
        params.append(customer)
    sql += " ORDER BY order_date, order_id"
    return pd.read_sql_query(sql, con, params=params, parse_dates=["order_date"])
