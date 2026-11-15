## Hint 1

Write the chain of calls for `power(2, 5)`: which calls are waiting at the moment `power(2, 0)` runs? How many is that for `n = 10**6`?

## Hint 2

For `fast_power` write the sequence of `n` values: `n, n // 2, n // 4, ...`. How many times can you halve a million before you reach 0?

## Hint 3

Draw the call tree of `fast_power(x, 8) * ...` with two calls per level: 1, 2, 4, 8 ... nodes per level. What is the total?
