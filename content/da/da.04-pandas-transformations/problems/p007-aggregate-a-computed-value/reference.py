import pandas as pd


def net_revenue_by_category(lines, products):
    """Net revenue (qty * unit_price * (1 - discount)) per category."""
    net = lines.merge(products[["product_id", "category"]], on="product_id", how="left", validate="m:1")
    net = net.assign(net_revenue=net["qty"] * net["unit_price"] * (1 - net["discount"]))
    return net.groupby("category", as_index=False)["net_revenue"].sum()
