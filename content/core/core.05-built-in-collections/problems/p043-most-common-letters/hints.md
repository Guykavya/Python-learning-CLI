## Hint 1

Count with a dict, skipping characters for which `ch.isalpha()` is `False`.

## Hint 2

Sort `(-count, letter)` tuples and take the first three with a slice.

## Hint 3

Lowercase the whole line first so `H` and `h` count together.
