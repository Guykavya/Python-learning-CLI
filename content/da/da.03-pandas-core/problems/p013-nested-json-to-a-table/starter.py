import pandas as pd


def orders_from_json(records):
    """One row per order line: id, customer, sku, qty."""
    return pd.json_normalize(records)
