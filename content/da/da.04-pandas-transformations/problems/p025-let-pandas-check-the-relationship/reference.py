import pandas as pd


def lookup_products(lines, products):
    """Every line with category and list_price; ValueError listing duplicated product ids."""
    try:
        return lines.merge(products[["product_id", "category", "list_price"]], on="product_id",
                           how="left", validate="m:1")
    except pd.errors.MergeError as err:
        ids = products["product_id"]
        dups = sorted(ids[ids.duplicated()].unique().tolist())
        raise ValueError(f"duplicated product_id in products: {dups}") from err
