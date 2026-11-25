## Walkthrough

The row at `2025-04-01 00:00` is exactly the end of the quarter, so `<` excludes it: 10 of the 11 rows remain. January has customers {1, 2} = 2, February {1, 2, 3} = 3, March {3, 1, 4, 2} = 4, so `[2, 3, 4]` and a sum of 9. The quarter has the customers {1, 2, 3, 4} = 4. The difference is 9 - 4 = 5: customer 1 is counted in three months, customers 2 and 3 in three and two. Months overlap because a customer returns, so distinct counts do not add up.

## The output

```text
[2, 3, 4]
9
4
10 11
5
```

## Complexity

Every step is one pass over a handful of rows; the lesson is about the grain, not the cost.

## Another way

Run the program line by line in a notebook and print the grain after each step; then compare with your hand trace.
