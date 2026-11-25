- **`drop_duplicates(subset=key)` without sorting.** It keeps the *first* row in the current order, which is arbitrary
  unless you sorted first.
- **`keep="first"` after an ascending sort.** That keeps the *oldest* row. Newest wins: ascending sort + `keep="last"`.
- **Returning the sorted frame.** The cleaning must not shuffle the table; `kept` stays in the original row order.
- **An unstable sort for ties.** The default `quicksort` does not promise to keep equal values in file order; use
  `kind="stable"`.
- **`idxmax` on a tie** picks the first row, not the last.
- **Forgetting the removed rows.** The log needs to say *what* was dropped, not only how many.
- **Resetting the index** of `kept` and `removed`. The labels tell the reader which rows they were.
