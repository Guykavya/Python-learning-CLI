## Approach

| Table | Question that fails | Column |
|---|---|---|
| 1 | a cell holds several values (`gift,rush`) | `tags`: not 1NF |
| 2 | `product_name` is fixed by `product_id` alone, only **part** of the key | `product_name`: not 2NF |
| 3 | `dept_name` is fixed by `dept_id`, which is not the key | `dept_name`: not 3NF |
| 4 | none: every column describes the customer | ok |

Answer:

```text
1: 1NF tags
2: 2NF product_name
3: 3NF dept_name
4: ok
```

Fixes: table 1 gets a separate `order_tags(order_id, tag)` table; table 2 moves the name to `products(product_id PK, name)`; table 3 moves it to `departments(dept_id PK, dept_name)`. After each split, a fact is stored **once**.

## Complexity

Not applicable.

## Another way

Ask the update question: "if this fact changes, how many rows must I edit?" More than one means a normal form is broken.

## Why it matters

Each broken form is a way for the data to contradict itself (problem 1). Normalising removes the possibility, instead of relying on code that remembers to update every copy.
