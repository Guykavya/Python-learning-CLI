## Hint 1

Run the attempt in your head with `n = 1` and the value `-5`. What do `largest` and `smallest`
hold after the loop? Now try `n = 0`. Which line runs that should not?

## Hint 2

Edge cases usually live at the ends of the allowed range: the smallest count, the largest count,
the smallest and largest values, and values exactly equal to each other or to a limit. Also ask:
what if the input is outside what the problem promised?

## Hint 3

For each edge case write three columns: input, correct output, what the attempt prints. A good
fix for `largest`/`smallest` is to start them from the **first** value read, not from 0.
For your checklist, think about: empty, one item, all same, negative, zero, largest, boundary,
exact output format.
