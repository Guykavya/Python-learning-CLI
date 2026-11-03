# Partition overwrite: re-running a day replaces only that day

A daily job writes the orders of one day into a partitioned dataset:

```
orders/
    order_date=2024-06-01/part-0.parquet
    order_date=2024-06-02/part-0.parquet
```

Yesterday's run had a bug, so you fix it and re-run 2024-06-01. What should happen?

- If the job just **adds** files (what `pq.write_to_dataset` does by default), the day now holds
  the old rows *and* the new rows. Revenue for 1 June doubles.
- If the job deletes the **whole** dataset first, every other day is lost.
- If it deletes the day's folder first and then crashes while writing, 1 June has **no** data at
  all until someone notices.

The safe pattern is **partition overwrite**: the run for a day *owns* that day's folder. It
builds the complete new contents somewhere else, then swaps them in for the old folder, and never
touches other days. Running it once or ten times gives the same result.

## Your task

In `solution.py` write:

```python
def write_day(rows: list[dict], root, day: str) -> int:
```

`rows` are cleaned orders (`id`, `city`, `status`, `amount` as `Decimal`, `created_at` as an
aware datetime) and `day` is `"YYYY-MM-DD"`.

1. Every row must belong to `day`: the **UTC** date of its `created_at` must equal `day`.
   Otherwise raise `ValueError` and change nothing.
2. If `rows` is empty, remove the folder `root/order_date=<day>` if it exists (the day now has
   no orders) and return `0`.
3. Otherwise make the folder `root/order_date=<day>` contain **exactly** these rows, in a single
   Parquet file, with this schema: `id` int64 (not null), `city` string, `status` string (not
   null), `amount` decimal128(10, 2) (not null), `created_at` timestamp("us", tz="UTC") (not null).
   The files must not contain an `order_date` column (the folder name holds it).
4. Build the new data **before** removing the old. If building or writing fails (for example
   pyarrow raises `pa.ArrowInvalid` for an amount with three decimal places), the old folder must
   still be there, unchanged.
5. Never change any other folder under `root`, and leave no temporary files or folders behind.
6. Return the number of rows written.

A safe way to swap folders that also works on Windows: write the new file into a temporary
folder such as `root/.tmp-order_date=<day>`, then `os.replace(folder, old)` to move the current
folder out of the way, `os.replace(tmp, folder)` to move the new one in, and finally
`shutil.rmtree(old)`. (pyarrow ignores names starting with `.` or `_` when it reads a dataset.)
Using `pq.write_to_dataset(..., existing_data_behavior="delete_matching")` is also accepted.

## Example

```python
write_day([o1, o2], "orders", "2024-06-01")    # 2   folder holds orders 1, 2
write_day([o5], "orders", "2024-06-02")        # 1
write_day([o2_fixed, o3], "orders", "2024-06-01")   # 2 folder holds orders 2 (fixed), 3
                                                   #   2024-06-02 is untouched
write_day([], "orders", "2024-06-01")          # 0   folder removed
write_day([o5], "orders", "2024-06-01")        # ValueError: o5 belongs to 2024-06-02
```
