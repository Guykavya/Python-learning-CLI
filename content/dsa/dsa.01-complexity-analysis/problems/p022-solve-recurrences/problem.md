# Solve the recurrences

A recurrence describes the running time of a recursive algorithm in terms of smaller inputs. For each one below,
give the Big-O solution and justify it, either with the master theorem from the chapter (when it applies) or with a
recursion tree (count the work level by level). Assume `T(1)` is a constant.

1. `T(n) = 2T(n/2) + n`
2. `T(n) = T(n/2) + 1`
3. `T(n) = 2T(n/2) + 1`
4. `T(n) = 4T(n/2) + n`
5. `T(n) = T(n/2) + n`
6. `T(n) = T(n - 1) + 1`
7. `T(n) = T(n - 1) + n`
8. `T(n) = 2T(n - 1) + 1`

Then match each of these to one recurrence above and explain the match:

- **(a)** Binary search on a sorted list.
- **(b)** The recursive Fibonacci-style function that calls itself twice on `n - 1` (a slightly simplified version of
  `fib`, which calls `n - 1` and `n - 2`).
- **(c)** A recursive sum of a list: add the first element to the sum of the rest, where "the rest" is passed as an
  index (no copying).
- **(d)** Merge sort: sort each half, then merge them in linear time.

Finally, explain in a few sentences why the master theorem cannot be used for recurrences 6 to 8.
