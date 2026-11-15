## Hint 1

For 3: the number of pairs among 200000 items is about `n^2 / 2`. Divide by `M`.

## Hint 2

For 5: what hash do `a`, `aa`, `aaa` get when every `a` counts as 0? For 6: if the hash function is known and fixed, one can search for two strings with equal hash in advance.

## Hint 3

For 4 and 6: a bigger modulus such as `2^61 - 1`, two independent `(B, M)` pairs, a random base chosen when the program starts, and comparing the strings after a match.
