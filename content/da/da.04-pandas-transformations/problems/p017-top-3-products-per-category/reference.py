import pandas as pd


def top_products(lines, products, n=3):
    """The n best-selling products of each category: category, product_id, revenue, rank."""
    rev = (lines.assign(revenue=lines["qty"] * lines["unit_price"])
                .groupby("product_id", as_index=False)["revenue"].sum())
    rev = rev.merge(products[["product_id", "category"]], on="product_id", how="left", validate="1:1")
    top = (rev.sort_values(["category", "revenue", "product_id"], ascending=[True, False, True])
              .groupby("category")
              .head(n))
    top = top.assign(rank=top.groupby("category").cumcount() + 1)
    return top[["category", "product_id", "revenue", "rank"]].reset_index(drop=True)
