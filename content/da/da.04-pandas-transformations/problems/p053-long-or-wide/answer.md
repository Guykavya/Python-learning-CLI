## Model answer

1. **Tidy means one fact per row.** Each variable (store, quarter, revenue) is a column, and each observation (the
   revenue of one store in one quarter) is a row. Then every question is a short, general operation:
   `df.groupby("quarter")["revenue"].sum()` gives the totals per quarter, `groupby("store_id")` the totals per store,
   a filter on `quarter` keeps a period. In the wide table "quarter" is hidden in the column **names**, so the same
   question needs a loop over columns or a reshape first. New data also fits without changing the shape: a new quarter
   adds rows, while in the wide table it adds a column and every piece of code that lists the columns must change.

2. **Wide is for reading.** People compare across a row easily: a grid with stores down the side and quarters across
   the top is the natural printed report or spreadsheet view. Some calculations also want a matrix: a correlation
   between stores, or a model that needs one column per feature (one-hot flags are a wide shape too).

3. (a) A chart: **long**. Plotting libraries map columns to x (`quarter`), y (`revenue`) and colour (`store_id`).
   (b) The meeting table: **wide**, made at the end with `pivot` or `pivot_table` (with `margins=True` for totals).
   (c) Storage: **long**. A file or database table that grows keeps a fixed set of columns; adding columns each
   quarter breaks every reader. (d) Total per quarter: **long**, then `groupby("quarter")`.

4. **Moving between them.** Wide to long with `melt(id_vars="store_id", var_name="quarter", value_name="revenue")`;
   long to wide with `pivot` (each pair once) or `pivot_table` (with an aggregation, when pairs repeat). After moving,
   check the shape (stores × quarters cells, long rows = cells that hold a value), check that a total is the same
   in both shapes, and decide what a missing cell means (no sales = 0, or unknown = `NaN`).

**Checklist: your answer should mention**
- [ ] tidy/long for analysis (each variable a column, each observation a row)
- [ ] wide for reading (reports, spreadsheets) and some matrix-shaped tools
- [ ] one fact per row
- [ ] melt/pivot (and `pivot_table` when pairs repeat)
- [ ] a check after reshaping (shape, totals, meaning of missing cells)
