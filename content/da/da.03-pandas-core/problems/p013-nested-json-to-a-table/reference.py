import pandas as pd


def orders_from_json(records):
    """One row per order line: id, customer, sku, qty."""
    flat = pd.json_normalize(
        records,
        record_path="items",
        meta=["id", ["customer", "name"]],
        errors="ignore",
    )
    flat = flat.rename(columns={"customer.name": "customer"})
    flat["id"] = flat["id"].astype("int64")
    return flat.reindex(columns=["id", "customer", "sku", "qty"])
