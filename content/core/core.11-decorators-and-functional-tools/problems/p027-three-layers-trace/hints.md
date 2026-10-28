## Hint 1

The line `@tag("b")` contains a **call**: `tag("b")` runs first and gives back a decorator. In
what order does Python evaluate the three decorator lines: top to bottom, or bottom to top?
And in what order does it **apply** the decorators it got?

## Hint 2

Rewrite the stack as one line: `word = tag("b")(twice(2)(tag("i")(word)))`. Python evaluates
`tag("b")`, `twice(2)`, `tag("i")` first (left to right), then applies the innermost decorator
first. Which `__name__` does each decorator see? `tag` copies the name with `wraps`; `twice` does not.

## Hint 3

At call time the outermost wrapper runs first. Its "in" line prints, then it calls the next
layer. `twice` calls the inner layer two times, and each time the inner `tag("i")` wrapper prints
its "in" and "out" lines around `body`. The "out" lines print on the way back, inner layer first.
