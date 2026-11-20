# Three loading strategies, counted

Chapter sections 10.2 to 10.6. A database has **4 orders** with **0, 1, 2 and 3 order lines** (6 lines in all). The same code loads all the orders and then reads `len(order.lines)` for each, under three loading strategies:

```python
select(Order).order_by(Order.id)                                        # A. lazy (the default)
select(Order).order_by(Order.id).options(joinedload(Order.lines))       # B. joinedload
select(Order).order_by(Order.id).options(selectinload(Order.lines))     # C. selectinload
```

For each strategy write:

- `statements`: how many SQL statements the database receives while the orders are loaded **and** all four `order.lines` are read;
- `rows`: how many **rows the database sends back** in total over all those statements (`joinedload` uses a `LEFT OUTER JOIN`, so an order with 3 lines comes back as 3 rows, and an order with 0 lines as 1 row).

Write your answer in `answer.txt`, one line per strategy:

```text
lazy: statements=<n> rows=<n>
joinedload: statements=<n> rows=<n>
selectinload: statements=<n> rows=<n>
```

Do not run it.

## After you answer

1. Why does `joinedload` return **7** rows although there are only 4 orders and 6 lines?
2. How would the statement count of lazy loading change with 400 orders? And of `selectinload`?
3. When is `joinedload` the better choice?
