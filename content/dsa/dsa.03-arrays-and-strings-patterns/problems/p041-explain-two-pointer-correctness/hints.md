## Hint 1

Fix `i`. The partners still in play are `a[i + 1], ..., a[j]`. Which of them gives the **largest** sum with
`a[i]`? If even that largest sum is below the target, can any smaller partner reach it?

## Hint 2

Draw the pairs as a triangle: row `i`, column `j`, only `i < j`. The move `i += 1` deletes a whole row of the
triangle that is still in play; `j -= 1` deletes a whole column. Your job is to show that the deleted row or
column contains no solution.

## Hint 3

A possible invariant: "If a solution pair `(p, q)` exists, then `i <= p` and `q <= j`." Check it before the
first pass (`i = 0`, `j = n - 1`). Then show: if `i == p`, the code never moves `i` (why?). If `j == q`, the
code never moves `j`. So the pointers stop on the pair at the latest when they both reach it.

```
before the loop: 0 <= p and q <= n - 1           -> true
i moves only when a[i] + a[j] < target:
    if i == p then a[p] + a[j] >= a[p] + a[q] = target   (j >= q, sorted)
    so i == p never moves -> invariant kept
same for j
```
