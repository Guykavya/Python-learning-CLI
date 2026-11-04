# Trace the sieve crossing off

This sieve prints, for every prime `p` it uses, the numbers that **this prime crosses off for the first time**
(numbers an earlier prime already crossed off are not listed). Predict **exactly** what it prints. Do not run it.

```python
n = 50
is_prime = [True] * (n + 1)
is_prime[0] = False
is_prime[1] = False

for p in range(2, n + 1):
    if p * p > n:
        break
    if is_prime[p]:
        newly = []
        for m in range(p * p, n + 1, p):
            if is_prime[m]:
                newly.append(m)
            is_prime[m] = False
        print(p, newly)

print("primes", sum(is_prime))
print("last", max(i for i in range(n + 1) if is_prime[i]))
```

Write your answer in `answer.txt`, one line per printed line. A line looks like `3 [9, 15]`: the prime, a space,
and the Python list repr.

## How to work

Start from `is_prime` all true except 0 and 1. For each `p`: stop if `p * p > 50`; skip if `p` was crossed off;
otherwise walk `p*p, p*p + p, ...` up to 50 and list those that are still marked prime.

## After you answer

1. Why does the walk start at `p * p` and not at `2 * p`? Which multiples of 5 below 25 were already crossed?
2. Which primes are used? Why is the loop over `p` allowed to stop at 7 for `n = 50`?
3. 45 is a multiple of 5, but it is not in the list for 5. Who crossed it off?
