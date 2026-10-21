## Hint 1

`y = x` does not copy anything. After it, how many int objects are there, and how many names?

## Hint 2

`y += 1` on an int cannot change the object (ints are immutable). It builds a new int and rebinds `y`.

## Hint 3

`==` asks "same value?". `is` asks "the very same object?" (same `id`). `1` and `1.0` have equal
values but different types.
