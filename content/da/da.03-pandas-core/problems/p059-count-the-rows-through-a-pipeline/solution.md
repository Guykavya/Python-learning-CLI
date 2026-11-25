## Approach

Keep a list of the surviving row labels after every step.

- Start: 10 rows (labels 0 to 9).
- `dropna(subset=["city"])`: only label 3 (`id` 3) has no city. 9 rows left.
- `drop_duplicates()`: labels 1 and 2 are identical in every column (`2, Delhi, 5`), so label 2 goes. Labels 5 and 6 share `id` 5 and `city` but differ in `qty` (4 and 6), so both stay. 8 rows left. One of them (label 4) has a missing `qty`, so the second number on that line is 1.
- `b[b["qty"] > 2]`: keep `qty` 3, 5, 4, 6, 8, 4. Label 4 (NaN) and label 7 (`qty` 1) go. 6 rows left (labels 0, 1, 5, 6, 8, 9).
- `drop_duplicates(subset=["id"], keep="last")`: `id` 5 appears at labels 5 and 6; the later one (label 6, `qty` 6) stays. 5 rows left.

Last lines: the ids are `[1, 2, 5, 7, 8]`, the quantities `[3.0, 5.0, 6.0, 8.0, 4.0]` (floats), and the labels `[0, 1, 6, 8, 9]`. The dtype of `qty` is `float64` and the original frame still has 10 rows because nothing was changed in place.

## Code

The expected output is in `expected.txt`, produced by running the program above.

## Complexity

Every step is a single pass over the rows (the duplicate steps hash each row or key): O(n) each.

## Another way

To make the loss visible in a real project, print `len(df)` after each step with `pipe`: `df.pipe(lambda d: (print(len(d)), d)[1])`, or keep a list of `(step name, rows left)` pairs. That is the same audit as the problem register of the chapter's project: nothing should disappear silently.
