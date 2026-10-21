## Hint 1

Run the starter on the example by hand or on the computer. Which student is missing? Which
numbers look wrong? Fix one thing at a time.

## Hint 2

Look closely at: the `range` that drives the loop; the condition that counts a present mark;
the division; the comparison with 75; and the `else` on the `for` loop.

## Hint 3

The five fixes: `enumerate(names, start=1)` instead of `range(1, len(names))`;
`mark in "Pp"` (or `mark.upper() == "P"`) instead of `mark == "P" or "p"`; `/` instead of
`//`; `< 75` instead of `<= 75`; and `if low == 0:` instead of a loop `else` that has no `break`.
