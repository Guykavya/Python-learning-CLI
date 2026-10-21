## Hint 1

Which of `a`, `b`, `c`, `d` refer to mutable objects? A function can never change the caller's int or string.

## Hint 2

After `items = items + [0]`, the name `items` refers to a new list. Every later line in that function works on the new list, not the caller's.

## Hint 3

`grid[0] = ...` replaces a slot in the caller's outer list; `row = [...]` inside a loop only rebinds the loop variable.

## Hint 4

In `extend_twice`, `+=` on a list mutates it in place, so the caller sees both extensions.
