- **Counting `isna()` after the replacement.** That includes values that were missing before. The count is of codes.
- **Changing the caller's frame.** `df[col] = df[col].mask(...)` on the input silently edits the raw data. Copy first.
- **Replacing a code in every column.** `0` is a code for *income* but a perfectly good value of `satisfaction` or a
  count. The codes belong to a column.
- **`df.replace(-1, np.nan)` on the whole table.** Same problem as above, and it also touches text columns.
- **Dropping the rows with codes.** The row may still hold good information in the other columns; we mask the cell.
- **Leaving out a column with no codes from `counts`.** A zero is information too ("we looked, there were none").
