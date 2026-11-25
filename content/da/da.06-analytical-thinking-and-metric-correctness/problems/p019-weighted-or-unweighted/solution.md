## Walkthrough

The groups are Delhi (1 job, mean 600.0), Jaipur (2 jobs, mean 150.0) and Pune (4 jobs, mean 250.0), in that order, so `[1, 2, 4]` and `[600.0, 150.0, 250.0]`. The simple mean is (600 + 150 + 250) / 3 = 333.33. The weighted mean is (600 + 300 + 1000) / 7 = 271.43, the same as the direct mean 1900 / 7, because weighting each group mean by its number of jobs gives back the sum of all values divided by the number of values. Delhi has one job but a full third of the vote in the simple mean, so it misses by 61.9.

## The output

```text
[1, 2, 4] [600.0, 150.0, 250.0]
333.33
271.43
271.43
61.9
```

## Complexity

Every step is one pass over a handful of rows; the lesson is about the grain, not the cost.

## Another way

Run the program line by line in a notebook and print the grain after each step; then compare with your hand trace.
