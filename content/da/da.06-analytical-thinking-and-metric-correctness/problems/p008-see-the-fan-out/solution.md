## Walkthrough

Job 1 has three lines, so it appears three times. The join has 7 rows but still 4 distinct jobs. The quote sum becomes 3000 + 400 + 1400 + 300 = 5100 instead of 2400. The mean after the join is 5100 / 7 = 728.57; the true mean is 2400 / 4 = 600.0, because the biggest job has the most lines and counts three times. `groupby("job_id").size()` lists the lines per job in job order: `[3, 1, 2, 1]`. Keeping one row per job restores the true sum, 2400.

## The output

```text
7 4
5100 2400
728.57 600.0
[3, 1, 2, 1]
2400
```

## Complexity

Every step is one pass over a handful of rows; the lesson is about the grain, not the cost.

## Another way

Run the program line by line in a notebook and print the grain after each step; then compare with your hand trace.
