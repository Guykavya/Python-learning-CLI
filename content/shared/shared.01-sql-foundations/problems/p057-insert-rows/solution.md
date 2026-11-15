## Approach

Step 1 is a multi-row `VALUES` insert with a column list; `customer_id` is omitted so SQLite assigns it. Step 2 is `INSERT ... SELECT DISTINCT`, filtered with `IS NOT NULL`. The order matters: the cities are read from the table as it is when step 2 runs.

## Code

```python
SCRIPT = """
INSERT INTO customers (name, city, joined)
VALUES ('Zoe', 'Lima', '2024-05-01'), ('Yan', NULL, '2024-05-02');

INSERT INTO city_list (city)
SELECT DISTINCT city FROM customers WHERE city IS NOT NULL;
"""
```

## Complexity

Each inserted row costs O(log n) per index (the primary key counts). `INSERT ... SELECT` scans `customers` once plus the dedupe work.

## Another way / portable SQL

`INSERT OR IGNORE INTO city_list SELECT city FROM customers WHERE city IS NOT NULL` also works (the primary key rejects repeats). MySQL spells it `INSERT IGNORE`, PostgreSQL `ON CONFLICT DO NOTHING`. Multi-row `VALUES` is standard in all three.
