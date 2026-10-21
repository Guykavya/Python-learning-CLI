## Hint 1

Line 1 keeps only some numbers: that is a **filter**, an `if` at the end of the comprehension.

## Hint 2

Line 2 keeps every number but changes some: that is a conditional expression at the front,
`n if n >= 0 else 0`.

## Hint 3

Line 3: a set comprehension `{n % 3 for n in nums}` removes repeats; `sorted(...)` makes it a list.
