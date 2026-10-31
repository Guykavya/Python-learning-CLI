## Hint 1

For each variable or parameter, say which of the two it is. What may you do with an `object` (what do all objects have in common)? What does the checker do when it meets an `Any`?

## Hint 2

`Any` switches checking off in **both** directions: you can use an `Any` value anywhere, and you can read any attribute from it. `object` is the opposite: it is a real type at the very top of the hierarchy. Everything fits **into** an `object`, but an `object` fits **nowhere** else unless you narrow it first.

## Hint 3

`len(a)` has a known result type, whatever `a` is. For line `L`, mypy only checks the *call sites* against the declared parameter types: `Any` and `object` both accept `123`. Whether the function body would crash at run time is not mypy's question here.
