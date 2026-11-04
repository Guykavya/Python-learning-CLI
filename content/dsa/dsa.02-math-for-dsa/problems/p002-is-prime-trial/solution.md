## Approach

If `n = a * b` with `a <= b`, then `a * a <= a * b = n`. So a composite number always has a divisor `a` with
`a * a <= n`. We only test `i = 2, 3, ...` while `i * i <= n`. If none divides `n`, it is prime. Numbers below 2
are not prime.

## Code

```python
q = int(input())
for _ in range(q):
    n = int(input())
    if n < 2:
        print("composite")
        continue
    i = 2
    prime = True
    while i * i <= n:
        if n % i == 0:
            prime = False
            break
        i += 1
    print("prime" if prime else "composite")
```

## Complexity

O(sqrt n) per query: at most about 31623 loop passes for `n = 10^9`. The whole input is about 3 million steps.
Trying all `d` up to `n` would be a thousand million steps per query.

## Another way

After handling 2 separately, test only odd `i` (step 2). That halves the work. Later you will see the sieve,
which answers "is it prime?" for every number up to a limit at once, and 6k +/- 1 wheels that cut the work to a third.
