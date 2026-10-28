## Hint 1

Write each stack as one line. `fib_a = counted(lru_cache(...)(fib_a))`: the counter is outside,
so it sees **every** call that goes through the name `fib_a`, including the ones the cache
answers. `fib_b = lru_cache(...)(counted(fib_b))`: the counter is inside, so it only sees calls
that the cache let through, the misses.

## Hint 2

With a cache, `fib(5)` computes each of `fib(5) .. fib(0)` once: 6 misses. Each miss with
`n >= 2` makes two calls. Count all calls: 1 outer call + 2 calls for each of n = 5, 4, 3, 2.
How many of those were hits? For `counted_plain`, which name does `plain`'s body call?
And `fib_b.calls` is not `fib_b.__wrapped__.calls`: when was it copied?
