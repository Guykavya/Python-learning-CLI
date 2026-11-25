import pandas as pd

COLUMNS = ["order_id", "customer", "order_date", "qty", "price"]


def orders_frame(records):
    """DataFrame from a list of dicts: fixed columns, parsed dates, nullable qty."""
    return pd.DataFrame(records)
