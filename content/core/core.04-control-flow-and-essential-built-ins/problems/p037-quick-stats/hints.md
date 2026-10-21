## Hint 1

The items from `split()` are strings. `max("10 9".split())` compares them as text and gives
`"9"`. How can you compare them as numbers?

## Hint 2

A generator expression converts as it goes: `sum(int(w) for w in words)`. When you also pass
`default=`, the generator expression needs its own brackets:
`min((int(w) for w in words), default=None)`.

## Hint 3

Print `none` when the result is `None`: `"none" if smallest is None else smallest`.
