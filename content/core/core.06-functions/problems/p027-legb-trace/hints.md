## Hint 1

Assignments create locals. A function that only **reads** a name finds it in an outer scope.

## Hint 2

`inner` has no `x` of its own in `read_outer`, so it finds the enclosing one. In `outer`, `inner` assigns `x`, so its `x` is local.

## Hint 3

`len` inside `shadow` is the local variable `len = 3`, not the built-in. Outside, the built-in is untouched.
