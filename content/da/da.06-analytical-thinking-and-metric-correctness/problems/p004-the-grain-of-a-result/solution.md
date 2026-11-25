## Walkthrough

The merge moves the table to the **line** grain: 6 rows, the three job columns repeated on each of them. `job_id` alone repeats (jobs 1 and 3 have several lines), the pair `(job_id, line_no)` does not, and `(city, item)` repeats because Pune/labour exists for jobs 1 and 3. The `groupby` produces one row per city, so `city` is a key of `by_city`. Pune has 2 + 3 = 5 lines and a repeated quote of 500x2 + 900x3 = 3700, which is not Pune's real quoted value (1400). After `drop_duplicates(subset=["job_id"])` one row per job remains: 3 rows, quote 500 + 300 + 900 = 1700. The last sum, 4000, is the inflated sum on the line grain.

## The output

```text
6
True False True
[1, 5] [300, 3700]
False
3 False 1700
4000
```

## Complexity

Every step is one pass over a handful of rows; the lesson is about the grain, not the cost.

## Another way

Run the program line by line in a notebook and print the grain after each step; then compare with your hand trace.
