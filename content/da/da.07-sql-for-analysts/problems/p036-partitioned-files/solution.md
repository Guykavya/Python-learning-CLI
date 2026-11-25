## Approach

Point `read_parquet` at a glob that matches every file below the folder, switch on `hive_partitioning`, and group by the recovered column. `**` matches any depth of folders, so several files per partition (or nested partitions) are all read.

## Code

```python
def revenue_by_country(con, folder):
    sql = f"""
        SELECT country, sum(amount) AS revenue
        FROM read_parquet('{folder}/**/*.parquet', hive_partitioning = true)
        GROUP BY country ORDER BY country
    """
    return con.execute(sql).fetchall()
```

## Complexity

One scan of the `amount` column of every file; with a filter on `country` DuckDB would skip the other folders ("partition pruning").

## Another way

`COPY (...) TO 'folder' (FORMAT parquet, PARTITION_BY (country))` writes a dataset like this. Choose a partition column that queries filter on and that has a moderate number of values (a month, a country). Partitioning by `user_id` would create thousands of tiny files and be slower, not faster.

## Pitfall to remember

On DuckDB 2.0, `hive_partitioning = true` and `= 1` both work (checked on the installed version); older versions differed, so use the explicit `true`.
