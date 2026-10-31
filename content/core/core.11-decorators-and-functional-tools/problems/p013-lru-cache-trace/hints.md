## Hint 1

`compute n` prints only on a miss. `fib(n - 1) + fib(n - 2)` calls the left side first, all the way down,
before the right side. By the time the right side is called, has its value already been stored?

## Hint 2

Keep a small table: the set of stored `n` values, a hits counter and a misses counter. Walk `fib(4)`:
4 miss, 3 miss, 2 miss, 1 miss, 0 miss, then `fib(1)` inside `fib(3)` is a hit, and `fib(2)` inside
`fib(4)` is a hit. `currsize` is the number of stored values. `cache_clear()` empties the store **and**
resets both counters.
