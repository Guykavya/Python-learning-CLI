import pandas as pd


def bought_product(customers, lines, product_id):
    """Customers who bought product_id at least once: customer columns, once each, original order."""
    buyers = lines.loc[lines["product_id"] == product_id, "customer_id"]
    return customers[customers["customer_id"].isin(buyers)].reset_index(drop=True)
