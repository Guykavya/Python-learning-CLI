# Let pandas check the relationship

Chapter section 6.7. Every merge assumes a relationship between the keys. Order lines to products is **many-to-one**:
many lines, at most one product row per id. `validate="m:1"` makes pandas check that **before** joining and raise
`pandas.errors.MergeError` if the product table breaks the promise. That error says *that* keys are duplicated, not
*which* ones; a good function tells the person who must fix the data exactly what to fix.

Write `lookup_products(lines, products)`.

- `lines` has `order_id`, `product_id`, `qty`, `unit_price`.
- `products` should have one row per `product_id`, with `category` and `list_price`.
- Return every line, in the original order, index `0, 1, 2, ...`, with the line columns followed by `category` and
  `list_price`. A line whose product is unknown is kept with missing values. The row count equals the number of lines.
- If `products` has a duplicated `product_id`, raise `ValueError` whose message contains **every duplicated id**
  (sorted, each once), for example `duplicated product_id in products: ['P002', 'P005']`. Use `validate="m:1"`, catch
  the `MergeError` and raise your own clearer error (`raise ValueError(...) from err`).

Do not change the inputs.

## Example

```python
import pandas as pd

lines = pd.DataFrame({"order_id": [1, 1, 2], "product_id": ["P001", "P002", "P009"],
                      "qty": [1, 2, 1], "unit_price": [10.0, 5.0, 7.0]})
products = pd.DataFrame({"product_id": ["P001", "P002"], "category": ["home", "toys"], "list_price": [10.0, 5.0]})
print(lookup_products(lines, products))

bad = pd.concat([products, products.tail(1)], ignore_index=True)
try:
    lookup_products(lines, bad)
except ValueError as e:
    print(e)
```

```text
   order_id product_id  qty  unit_price category  list_price
0         1       P001    1        10.0     home        10.0
1         1       P002    2         5.0     toys         5.0
2         2       P009    1         7.0      NaN         NaN
duplicated product_id in products: ['P002']
```
