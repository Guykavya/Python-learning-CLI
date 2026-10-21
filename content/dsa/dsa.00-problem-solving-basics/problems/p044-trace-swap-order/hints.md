## Hint 1

In `a, b = b, a + b`, Python works out **both** values on the right side first, using the old `a` and `b`,
and only then stores them. What are the right-hand values when `a = 0` and `b = 1`?

## Hint 2

In the second loop, `a = b` runs first. When `b = a + b` runs on the next line, what value does `a` have now?
Compare it with `b`.

## Hint 3

After `a = b`, the two variables are equal, so `b = a + b` is the same as `b = b + b`: `b` doubles every step,
and `a` is always the previous `b`.
