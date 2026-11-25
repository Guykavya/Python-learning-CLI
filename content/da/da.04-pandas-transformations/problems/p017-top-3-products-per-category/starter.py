import pandas as pd


def top_products(lines, products, n=3):
    """The n best-selling products of each category: category, product_id, revenue, rank."""
    return pd.DataFrame(columns=["category", "product_id", "revenue", "rank"])
