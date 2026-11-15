# COUNT(*), COUNT(col) and COUNT(DISTINCT col)

`COUNT` has three forms that look alike and answer three different questions:

- `COUNT(*)` counts **rows**.
- `COUNT(city)` counts rows where `city` is **not NULL**.
- `COUNT(DISTINCT city)` counts the **different** non-NULL values.

Table `customers` (the `city` column may be NULL):

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
INSERT INTO customers VALUES (1,'Asha','Pune'),(2,'Bala','Delhi'),(3,'Chitra',NULL),(4,'Dev','Pune'),(5,'Esha',NULL),(6,'Farid','Mumbai');
```

Write one query that returns **one row** with three columns, in this order and with these names:

| column | meaning |
|---|---|
| `total_rows` | how many customers exist |
| `with_city` | how many customers have a city |
| `distinct_cities` | how many different cities there are |

No `ORDER BY` is needed (one row only).

**Example.** If the table had the cities `Pune, Pune, NULL`, the answer row would be `(3, 2, 1)`.
For the table above the answer is `(6, 4, 3)`. Check it by hand first: two NULL cities, and Pune appears twice.

Put your SQL in `solution.py` (copy `starter.py` first).
