## Hint 1

Write out the indices: h0 e1 l2 l3 o4 (space)5 w6 o7 r8 l9 d10.

## Hint 2

`find` gives the first position or -1. `rfind` gives the last position, still counted from the left. The third argument of `replace` limits the number of replacements.

## Hint 3

All matching is case-sensitive. `s.upper().find("O", 5)` starts looking at index 5 of the uppercase string.
