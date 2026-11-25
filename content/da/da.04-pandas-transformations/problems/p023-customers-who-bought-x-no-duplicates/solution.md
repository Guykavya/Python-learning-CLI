## Approach

Filter the lines to the product, take the customer ids, and keep the customers whose id is among them. A boolean mask
keeps each customer row at most once, never adds columns, and keeps the customer order. Ids on the lines that are not
customers (orphans) cannot appear, because we filter the customer table.

## Code

```python
import pandas as pd


def bought_product(customers, lines, product_id):
    buyers = lines.loc[lines["product_id"] == product_id, "customer_id"]
    return customers[customers["customer_id"].isin(buyers)].reset_index(drop=True)
```

## Complexity

O(L + C): one pass over L lines to filter, a hash set of the buyers, one pass over C customers.

## Another way

`customers.merge(buyers.drop_duplicates().to_frame(), on="customer_id", how="inner")` is the semi-join written as a
merge. The `drop_duplicates()` is essential: without it, a customer who bought three times comes out three times
(fan-out, Ch. 6.8). An inner merge also keeps the left order in pandas 3.
