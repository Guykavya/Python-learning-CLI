## Approach

One stable bucket pass per digit, from the least significant to the most significant. After the pass for the top digit, the order is fully sorted.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
exp = 1
biggest = max(a)
while biggest // exp > 0:
    buckets = [[] for _ in range(10)]
    for x in a:
        buckets[(x // exp) % 10].append(x)
    a = [x for bucket in buckets for x in bucket]
    exp *= 10
print(" ".join(map(str, a)))
```

## Complexity

O(d * (n + b)) time for `d` digits in base `b` (here `d <= 10`, `b = 10`), O(n + b) memory. For fixed-size integers it is linear in `n`.

## Another way

A bigger base needs fewer passes: base 1000 gives 3 passes for numbers up to 10^9 with 1000 buckets. A bit-shift version with base 256 (`(x >> (8 * p)) & 255`) is the usual form for 32-bit integers.
