- **`nunique(dropna=False)` or `value_counts(dropna=False)`.** That counts "missing" as a value. The task says
  *non-missing* distinct values, and `top` is never "missing".
- **Choosing `top` with `idxmax()` and thinking it is the smallest on ties.** `idxmax` returns the first label in the
  `value_counts` order, which depends on the order of appearance. Sort the tied labels.
- **Calling `.str` on a numeric column.** `df["age"].str.strip()` raises `AttributeError`. Check the dtype first.
- **Flagging every text column.** `city` contains no numbers at all, so the "number-like" test must say no and
  `suspect_text` must be `0`. Do not count the non-numbers of a column that was never meant to be numeric.
- **Forgetting that `""` is a value.** An empty string is not missing for pandas (`isna()` is `False`), but it does not
  parse as a number: it is one of the suspects.
- **Changing `df`** (for example replacing `""` by NA to count it). Work on copies or on the extracted `present`.
