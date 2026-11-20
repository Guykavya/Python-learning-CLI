## Hint 1

Go table by table and ask the three questions in order: any cell with several values? Any column that needs only part of a composite key? Any non-key column that is determined by another non-key column?

## Hint 2

Table 2: the key is `(order_id, product_id)`. Does `product_name` change when `order_id` changes? No: it follows `product_id` alone. Table 3: `dept_name` follows `dept_id`, not `emp_id` directly.

## Hint 3

Table 1: `tags` holds `"gift,rush"`: a list in one cell. Table 4 has a single-column key and every column describes the customer: nothing to fix.
