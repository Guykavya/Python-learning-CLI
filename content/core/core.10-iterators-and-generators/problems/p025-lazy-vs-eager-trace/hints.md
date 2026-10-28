## Hint 1

A list comprehension builds the whole list **before** the `=` assignment finishes. A generator
expression builds nothing at first. When does it call `double` for each item?

## Hint 2

The last part is a detail: in a generator expression, the **first** `for ... in <something>` part
is evaluated at once, when the expression is created. Everything else waits. So when is
`source()` called: at `c = ...`, or at `next(c)`?
