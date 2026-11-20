## Hint 1

`i = 1`: `k = 0`, compare `s[1] = b` with `s[0] = a`: no match, `k` stays 0, `path = [0]`. `i = 2`: compare `s[2] = a` with `s[0] = a`: match, `k = 1`.

## Hint 2

`i = 3`: `k = 1`, compare `s[3] = c` with `s[1] = b`: mismatch, fall back to `pi[0] = 0`, so `path = [1, 0]`. Then `c` against `s[0] = a`: no match. `pi[3] = 0`.

## Hint 3

At `i = 7`, `k = 3` (the border `aba`). The letter `b` is compared with `s[3] = c`: mismatch. Fall back to `pi[2]`. Which value is that, and does `b` match the letter at that position?
