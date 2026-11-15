## Approach

Each round of `n = n & (n - 1)` removes exactly one 1-bit. When `n` is 0 there are no bits left. The number of rounds is the popcount.

## Code

```python
import sys

data = sys.stdin.read().split()
q = int(data[0])
out = []
for token in data[1:1 + q]:
    n = int(token)
    count = 0
    while n:
        n &= n - 1
        count += 1
    out.append(count)
print("\n".join(map(str, out)))
```

## Complexity

O(popcount) per number, at most 62 rounds. Looking at all bit positions one by one (`n % 2`, then `n //= 2`) costs
62 rounds every time, even for `n = 2^61` which has a single 1-bit.

## Another way

`bin(n).count("1")` or `n.bit_count()` (Python 3.10+). Or the loop `while n: count += n & 1; n >>= 1`, which looks at every bit.
