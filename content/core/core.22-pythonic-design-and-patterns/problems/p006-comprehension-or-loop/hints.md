## Hint 1

For each function ask: am I **building** something, **asking** something, or **doing** something
(side effect) or **escaping early**? Which of the eight are "doing" or "escaping"? Those need
no change. For `any_big`: what is the difference between `[x for ...]` and `(x for ...)`
for a stream of a million numbers?

## Hint 2

```
squares_of_evens: [n * n for n in nums if n % 2 == 0]
word_lengths    : {w: len(w) for w in text.split()}
count_long      : sum(1 for w in words if len(w) > n)
any_big         : any(x > limit for x in items)
flatten         : [x for row in matrix for x in row]       (read left to right like loops)
log_and_double, first_duplicate : keep as they are
pythagorean_triples : two loops (a, b); compute c = isqrt(a*a + b*b); keep if c <= n and c*c == a*a + b*b
```
`from math import isqrt` is the exact integer square root.
