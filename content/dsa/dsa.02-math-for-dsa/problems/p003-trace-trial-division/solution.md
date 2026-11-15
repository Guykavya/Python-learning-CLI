## Walkthrough

| n | loop condition with `i = 2` | what happens |
|---|---|---|
| 1 | `4 <= 1` false | no tries; returns `True`, but `n > 1` fails so it prints `not prime` |
| 2 | `4 <= 2` false | no tries; prime |
| 9 | `4 <= 9`, then `9 <= 9` | tries 2 (remainder 1), then 3 divides 9, returns `False` |
| 17 | 4, 9, 16 are `<= 17`; 25 is not | tries 2, 3, 4, then no divisor: prime |
| 30 | `4 <= 30` | 2 divides 30 straight away: not prime |

Note 9: the test `i * i <= n` is `<=`, so `3 * 3 = 9` still gets its turn. With `<` the program would print
"no divisor found" for 9.

## Key idea

The loop runs only while `i * i <= n`, so for a prime `n` it makes about `sqrt(n)` tries. For 17 that is 3 tries
(2, 3, 4); for `n = 10^9 + 7` it is about 31623 tries, not a billion.
