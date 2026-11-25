## Hint 1

If you read one file with `read_parquet('orders/country=IN/part-0.parquet')`, is there a `country` column? What option tells DuckDB to build it from the folder names, and which glob pattern finds all the files in all the partition folders (including several files in one folder)?

## Hint 2

```text
read_parquet('<folder>/**/*.parquet', hive_partitioning = true)
SELECT country, sum(amount) FROM that GROUP BY country ORDER BY country  -> fetchall()
```
