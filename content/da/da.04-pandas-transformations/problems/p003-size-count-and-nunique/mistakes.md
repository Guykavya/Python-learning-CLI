- **`count()` for `lines`.** `count()` skips missing values, so a line with a missing product or coupon would not be
  counted. Rows are counted by `size()`.
- **`size()` for `with_coupon`.** That counts every line, coupon or not.
- **`nunique()` for `with_coupon`.** That counts different coupon *codes*: two lines with `SAVE10` give 1, not 2.
- **`count()` for `distinct_products`.** A customer who bought `P1` twice has 2 product lines but 1 product.
- **Forgetting `as_index=False`.** Then `customer_id` is the index, not a column.
