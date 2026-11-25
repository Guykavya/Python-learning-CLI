- **Counting the helper column too.** Add `_filled` *after* you have counted, or the count includes itself.
- **Sorting only by `updated_at`.** That is problem 16's rule ("newest wins"). Here completeness comes first.
- **Sorting `_filled` and `updated_at` the wrong way round.** The first sort key decides first; completeness is first.
- **`keep="first"` after an ascending sort.** That keeps the *worst* row.
- **Returning the sorted frame.** Keep the original row order and labels.
- **Counting only some columns.** The rule counts all cells, including the key and `updated_at` (they are never
  missing, so they add the same amount to every row).
- **An unstable sort** loses the "later row wins" rule on full ties.
