import pandas as pd


def attach_store_names(orders, stores):
    """Every order with city_customer, city_store and region."""
    out = orders.merge(stores, left_on="store_id", right_on="sid", how="left",
                       suffixes=("_customer", "_store"), validate="m:1")
    return out.drop(columns="sid")
