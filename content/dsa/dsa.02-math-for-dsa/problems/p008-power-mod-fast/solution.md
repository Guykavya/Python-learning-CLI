## Approach

Write `b` in binary. `a^b` is the product of `a^(2^k)` over the positions `k` where `b` has a 1-bit. We keep
`base = a^(2^k)` by squaring each round, and multiply it into `result` when the current lowest bit of `b` is 1.
Everything is reduced mod `m` after each multiplication.

## Code

```python
q = int(input())
for _ in range(q):
    a, b, m = (int(x) for x in input().split())
    result = 1 % m
    base = a % m
    while b > 0:
        if b % 2 == 1:
            result = result * base % m
        base = base * base % m
        b //= 2
    print(result)
```

## Complexity

O(log b) multiplications: at most about 60 per query for `b = 10^18`. The numbers stay below `m^2`.

## Another way

Recursion: `power(a, b) = 1 if b == 0`, `power(a, b // 2) ** 2 % m` if `b` is even, and
`a * power(a, b - 1) % m` if odd. The built-in `pow(a, b, m)` does the same, and is what you would use in
real code.
