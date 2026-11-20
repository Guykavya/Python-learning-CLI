## Approach

```python
import sys

data = sys.stdin.read().split()
t = int(data[0])
out = []
for i in range(t):
    a = int(data[1 + 3 * i])
    b = int(data[2 + 3 * i])
    p = int(data[3 + 3 * i])
    if b % p == 0:
        out.append("-1")
    else:
        out.append(str(a % p * pow(b, p - 2, p) % p))
print("\n".join(out))
```

Example: `a = 6, b = 3, p = 7`: `pow(3, 5, 7) = 243 % 7 = 5`, then `6 * 5 % 7 = 2`. For `10 7 7`: `7 % 7 == 0`, so `-1`.

## Complexity

`O(t log p)`.

## Another way

`pow(b, -1, p)` does the same with the extended Euclid algorithm and also works when `p` is not prime, as long as `b` and `p` share no factor (it raises `ValueError` otherwise).
