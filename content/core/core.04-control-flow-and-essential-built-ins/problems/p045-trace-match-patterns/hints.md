## Hint 1

Cases are tried top to bottom; the first match wins. A guard (`if ...`) must also be true.

## Hint 2

`["take", *things]` captures all remaining words into a list. `*_` matches the rest without
keeping it.

## Hint 3

`int(n)` matches integers only; `"7"` is a string. `(a, b)` is a sequence pattern of length 2.
