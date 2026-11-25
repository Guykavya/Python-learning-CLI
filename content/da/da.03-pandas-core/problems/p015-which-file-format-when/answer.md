## Model answer

1. **Excel (`.xlsx`)**, written with `to_excel(index=False)`. A manager opens it, filters it, and sees formatted numbers. Excel is for **people**; do not use it as a storage format for scripts (slow, limited rows, types guessed).

2. **Parquet** (`to_parquet`). It stores the **dtypes with the data**: dates stay dates, the nullable integers stay integers, text codes stay text with their zeros. A CSV would lose all of that and the next script would have to guess again ("CSV loses types").

3. **Parquet.** It is **columnar**: the reader can load only the three columns it needs, and the file is compressed, so it is small and fast. A CSV must be read through every column of every row, as text.

4. **JSON**, flattened with `pd.json_normalize` (use `record_path` for the item list and `meta` for the order fields). JSON is the format for **nested** data; a flat CSV cannot hold a list inside a cell.

5. **Query the database**: `pd.read_sql_query("... WHERE ... ?", con, params=...)`. The database already has the data, indexes and types, so ask it for just those rows instead of exporting everything to a file and filtering in pandas.

**Checklist: your answer should mention**
- [ ] CSV loses types (everything is text; the reader guesses)
- [ ] Parquet keeps types and is columnar (fast to read a few columns, compressed)
- [ ] Excel is for people, not for scripts
- [ ] JSON is for nested data (`json_normalize`)
- [ ] if the data is in a database, query it and let it filter (parameters, not f-strings)
