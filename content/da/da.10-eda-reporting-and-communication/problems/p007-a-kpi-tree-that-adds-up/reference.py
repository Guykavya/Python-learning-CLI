import pandas as pd


def revenue_tree(orders):
    g = orders.groupby("month").agg(active=("customer_id", "nunique"), n_orders=("amount", "size"),
                                    revenue=("amount", "sum")).sort_index()
    g["orders_per_active"] = g["n_orders"] / g["active"]
    g["avg_order_value"] = g["revenue"] / g["n_orders"]
    return g[["active", "orders_per_active", "avg_order_value", "revenue"]]
