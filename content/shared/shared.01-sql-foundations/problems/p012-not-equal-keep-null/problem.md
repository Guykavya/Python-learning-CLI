# Not equal, but keep the unknowns

The marketing team wants to send a flyer to everyone **who is not known to live in Pune**. A customer
with no city on file (NULL) must be included: we do not know that they live in Pune.

```sql
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT,            -- NULL when unknown
  joined      TEXT NOT NULL    -- 'YYYY-MM-DD'
);
INSERT INTO customers VALUES
 (1, 'Asha', 'Pune',  '2023-01-10'),
 (2, 'Ben',  NULL,    '2023-02-03'),
 (3, 'Chen', 'Delhi', '2023-02-20'),
 (4, 'Dia',  NULL,    '2023-04-01'),
 (5, 'Eli',  'Pune',  '2023-05-12'),
 (6, 'Fay',  'Goa',   '2023-06-30');
```

Return the `name` of every customer whose city is **not 'Pune' or is unknown**. One column, `name`.
Row order does not matter. Put the SQL in `QUERY`.

**Example.** On this data, `WHERE city <> 'Pune'` returns only Chen and Fay and silently drops Ben and Dia. Your result
must have **4 names**.
