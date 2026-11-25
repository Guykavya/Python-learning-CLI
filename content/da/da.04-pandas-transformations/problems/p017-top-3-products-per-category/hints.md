## Hint 1

Work in steps. What is the grain of the answer: lines or products? Once you have one row per product with its revenue
and category, in what order must the rows stand so that "the first 3 rows of each category" are the right ones,
including the tie between two products with the same revenue?

## Hint 2

```text
rev = lines.assign(revenue=qty*unit_price).groupby("product_id", as_index=False)["revenue"].sum()
rev = rev.merge(products[["product_id", "category"]], on="product_id", how="left", validate="1:1")
top = rev.sort_values(["category", "revenue", "product_id"], ascending=[True, False, True])
         .groupby("category").head(n)
top["rank"] = top.groupby("category").cumcount() + 1
select the four columns, reset_index(drop=True)
```
