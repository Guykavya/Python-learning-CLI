# Explain: when does an index help?

Your bookstore database has an `orders` table with 2 million rows:

```sql
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
```

A teammate says "the customer page is slow, let's index everything". You run `EXPLAIN QUERY PLAN` (SQLite 3.46) on some queries.
The lines starting with `>` are real output of the tool.

```
> EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id = 7;
SCAN orders

> EXPLAIN QUERY PLAN SELECT * FROM orders WHERE order_id = 7;
SEARCH orders USING INTEGER PRIMARY KEY (rowid=?)
```

You then run `CREATE INDEX idx_orders_customer ON orders(customer_id);` and repeat the first query, and also try these:

```
> SELECT * FROM orders WHERE customer_id = 7;
SEARCH orders USING INDEX idx_orders_customer (customer_id=?)

> SELECT * FROM orders WHERE customer_id + 0 = 7;
SCAN orders

> SELECT * FROM orders WHERE substr(ordered, 1, 7) = '2024-03';
SCAN orders

> SELECT order_id FROM orders WHERE customer_id = 7 ORDER BY ordered;
SEARCH orders USING INDEX idx_orders_customer (customer_id=?)
USE TEMP B-TREE FOR ORDER BY
```

Answer in your own words (150-400 words):

1. What is the difference between `SCAN` and `SEARCH`, and why is the first query so much faster after the index?
2. Why do `customer_id + 0 = 7` and `substr(ordered, 1, 7) = ...` still scan?
3. Which index would remove the `USE TEMP B-TREE FOR ORDER BY` line in the last query?
4. Give two costs of adding an index, and one query in this scenario where an index would **not** help.

Write your answer in `answer.md`, then compare with the model answer.
