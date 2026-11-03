## Hint 1

`load_raw` is plain `sqlite3`: which statement creates the table only the first time, and
which method inserts a whole list of rows with `?` parameters? For `build_clean`, first write
the `SELECT` alone and run it in a SQLite shell or with `conn.execute(...).fetchall()` until
every column looks right; then put `CREATE TABLE clean_orders AS` in front. Which `WHERE`
condition keeps `json_extract` away from broken text?

## Hint 2

```sql
DROP TABLE IF EXISTS clean_orders;
CREATE TABLE clean_orders AS
SELECT CAST(json_extract(payload, '$.id') AS INTEGER) AS id,
       lower(trim(json_extract(payload, '$.customer.email'))) AS email,
       NULLIF(trim(json_extract(payload, '$.customer.city')), '') AS city,
       ...
       CAST(ROUND(CAST(json_extract(payload, '$.amount') AS REAL) * 100) AS INTEGER) AS amount_cents,
       json_array_length(payload, '$.items') AS item_count
FROM raw_orders
WHERE json_valid(payload);
```

In Python run the two statements with two `conn.execute` calls, then `conn.commit()`.
