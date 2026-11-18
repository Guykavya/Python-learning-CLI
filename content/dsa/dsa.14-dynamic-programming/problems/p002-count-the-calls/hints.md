## Hint 1

For the naive function, `fib(0)` and `fib(1)` make one call each (the body runs, hits the base case, returns). For `n >= 2`: `C(n) = 1 + C(n - 1) + C(n - 2)`. So `C(2) = 1 + 1 + 1 = 3`. Continue the table up to `C(6)`. The values `fib(n)` are the usual `0, 1, 1, 2, 3, 5, 8`.

## Hint 2

For `fib_memo(6)` on an empty notebook, the **left** chain `6 -> 5 -> 4 -> 3 -> 2 -> 1` is all misses, and `fib_memo(2)` also asks `fib_memo(0)`, a miss. Then every **right-hand** call (`fib_memo(1)` from 3, `fib_memo(2)` from 4, `fib_memo(3)` from 5, `fib_memo(4)` from 6) is a hit. Count misses + hits. How many keys are now in the notebook?

## Hint 3

`calls` is reset to 0 before `again` and `next`, but the notebook is **not**. `fib_memo(6)` is now a single hit. `fib_memo(7)` is a miss that asks `fib_memo(6)` and `fib_memo(5)`: are those hits or misses? It also adds one new key.
