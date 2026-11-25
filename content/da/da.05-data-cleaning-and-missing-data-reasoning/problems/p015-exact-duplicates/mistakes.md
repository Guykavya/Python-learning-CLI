- **Calling `reset_index(drop=True)`.** The task keeps the original labels; they show which rows survived.
- **`n_removed = clean.duplicated().sum()`.** That counts duplicates left in the result (zero). Count the marks on the
  input.
- **Expecting `Pune` and `pune` to match.** Exact means exact; case folding is a separate, earlier cleaning step.
- **Believing missing values are never equal.** For `duplicated` they are equal: two rows that are both missing in the
  same columns and equal elsewhere are duplicates.
- **Using `subset=` for a key.** That is "duplicates by key" (next problem). Here all columns count.
- **Returning a NumPy integer.** Wrap the count in `int(...)`.
