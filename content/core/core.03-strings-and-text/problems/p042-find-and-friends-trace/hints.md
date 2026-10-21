## Hint 1

Indices: a0 -1 b2 -3 c4. `find` with a start argument begins searching at that index.

## Hint 2

`find` returns -1 when it fails, and -1 is a valid index. What is `s[-1]`?

## Hint 3

The empty string is found at every gap between characters, including both ends. A string of length 5 has 6 gaps (0 to 5). `count` with start and end looks only inside `s[start:end]`.
