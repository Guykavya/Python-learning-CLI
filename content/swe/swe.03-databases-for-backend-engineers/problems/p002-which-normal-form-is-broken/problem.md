# Which normal form is broken?

Chapter section 3.3 to 3.5. For each of the four tables below, the **primary key** is given. Decide whether the table is in good shape, or which rule it breaks first (check in this order: `1NF`, then `2NF`, then `3NF`), and **which column** causes the problem.

```text
Table 1: orders(order_id PK, customer, tags)
  1 | Asha  | "gift,rush"
  2 | Ravi  | "rush"

Table 2: order_lines(order_id, product_id, product_name, qty)      PK = (order_id, product_id)
  1 | 10 | Tea    | 2
  1 | 11 | Coffee | 1
  2 | 10 | Tea    | 5

Table 3: employees(emp_id PK, dept_id, dept_name)
  1 | 7 | Sales
  2 | 7 | Sales
  3 | 9 | Support

Table 4: customers(customer_id PK, name, email)
  1 | Asha | asha@x.com
  2 | Ravi | ravi@x.com
```

Rules to apply:

- `1NF` is broken when a cell holds **more than one value** (a list in a text field).
- `2NF` is broken when a column depends on **part** of a composite key only.
- `3NF` is broken when a non-key column depends on **another non-key column** (a transitive dependency).

Write your answer in `answer.txt`, one line per table:

```text
1: <1NF or 2NF or 3NF or ok> <column>
```

For a table that is fine write `4: ok` (no column).

## After you answer

1. For table 2: which column tells you the product name, and what is it really a fact about?
2. For table 3: what must you change in two rows if the Sales department is renamed?
3. How would you split each broken table?
