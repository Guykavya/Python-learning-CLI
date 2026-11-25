# Partitioned files

Chapter section 9.4. A big table is often stored as a **folder of files**, one folder per value of a partition column. The folder
names carry the value: `orders/country=IN/part-0.parquet`, `orders/country=US/part-0.parquet`. The files themselves do **not**
contain the `country` column. With `hive_partitioning = true`, DuckDB reads the folder names back as a normal column (and skips
folders a filter on that column excludes).

Write

```python
def revenue_by_country(con, folder):
    ...
```

`con` is an open DuckDB connection and `folder` the path (a string) of the dataset folder. The files inside have the columns
`order_id` and `amount` only. Return a **list of tuples** `(country, revenue)` with the total `amount` per country, **sorted by
country**. A country folder may hold more than one file. The query must use `hive_partitioning`.

```python
import duckdb, pandas as pd, pathlib
base = pathlib.Path("orders")
for country, df in {
    "IN": pd.DataFrame({"order_id": [1, 2], "amount": [499, 3999]}),
    "US": pd.DataFrame({"order_id": [3], "amount": [499]}),
}.items():
    (base / f"country={country}").mkdir(parents=True, exist_ok=True)
    df.to_parquet(base / f"country={country}" / "part-0.parquet", index=False)
con = duckdb.connect()
# from solution import revenue_by_country
print(revenue_by_country(con, "orders"))          # [('IN', 4498), ('US', 499)]
```

## Example

The dataset above has two partitions. The result is `[('IN', 4498), ('US', 499)]`: the country values come from the folder names.
