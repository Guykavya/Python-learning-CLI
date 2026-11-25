import pandas as pd

COLUMNS = ["order_id", "customer", "order_date", "qty", "price"]


def orders_frame(records):
    """DataFrame from a list of dicts: fixed columns, parsed dates, nullable qty."""
    df = pd.DataFrame(records, columns=COLUMNS)
    df["order_id"] = df["order_id"].astype("int64")
    df["customer"] = df["customer"].astype("str")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["qty"] = df["qty"].astype("Int64")
    df["price"] = df["price"].astype("float64")
    return df
