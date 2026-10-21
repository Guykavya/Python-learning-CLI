## Hint 1

Break it into two questions. (a) Given a number `x`, how do you decide whether it is prime?
(b) How do you walk through numbers, count the primes, and stop at the `k`-th one? Solve (b) with
a slow version of (a) first and check small `k` by hand.

## Hint 2

Speeding up (a): if `x = a * b` with `a <= b`, then `a * a <= x`. So if no `d` with `d * d <= x`
divides `x`, then `x` is prime. That cuts 200000 checks down to about 450. Also, after 2, every
prime is odd: handle 2 separately, then test only odd candidates, and divide only by odd `d`.

## Hint 3

```
if k == 1: print 2 and stop
count = 1          # 2 is counted
x = 1
while count < k:
    x += 2
    is_prime = True
    d = 3
    while d * d <= x:
        if x % d == 0: is_prime = False; break
        d += 2
    if is_prime: count += 1
print x
```
Check by hand: for `k = 3` the candidates are 3 (prime, count 2), 5 (prime, count 3), stop, print 5.
