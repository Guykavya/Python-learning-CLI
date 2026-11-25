# Verify a query without running it

Chapter section 9.6. You cannot run the Power Query offline, but you **can compare its output with the pandas output** by comparing a few **control numbers**: the row count, the column names, the sums of the numeric columns, the blanks per column and the distinct count of the key columns. Power Query cannot run offline; this problem checks the numbers and the steps in pandas, not the Power Query objects.

Write two functions.

**`fingerprint_table(df, keys=())`** returns a dict with these entries, **in this order**:

- `rows`: the number of rows;
- `columns`: the list of column names;
- `sum(<c>)` for each numeric column `c` (in column order): the sum rounded to 4 decimals, as a float;
- `blank(<c>)` for **every** column: the number of missing values (`isna`), as an int;
- `distinct(<k>)` for each key `k` in `keys`: the number of distinct values, as an int.

**`compare_fingerprints(a, b)`** returns a list of plain-words differences, in this order: for each entry of `a` (in order) that is missing from `b`: `"<key>: only in the first"`; that differs: `"<key>: <a value> against <b value>"`; then for each entry only in `b`: `"<key>: only in the second"`. An empty list means the two tables have the same fingerprint.

## Example

`rows: 120 against 119` and `sum(revenue): 5230.5 against 5100.25`: the query dropped a row and its revenue.
