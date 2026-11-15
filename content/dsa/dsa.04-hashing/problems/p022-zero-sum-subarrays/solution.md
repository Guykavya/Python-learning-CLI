## Approach

Two equal prefix sums enclose a block with sum 0. While walking, keep a table of how often each prefix sum occurred. For
the new prefix sum `s`, add `seen[s]` to the answer (one subarray per earlier equal prefix), then record `s`.
The table starts with `{0: 1}` for the empty prefix before the first element.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

seen = {0: 1}
s = 0
answer = 0
for x in a:
    s += x
    answer += seen.get(s, 0)
    seen[s] = seen.get(s, 0) + 1
print(answer)
```

## Complexity

O(n) time, O(n) memory.

## Another way

Compute all prefix sums, then take `c * (c - 1) // 2` for every prefix value that occurs `c` times. It is the same count
in a different order. The brute force with two loops and a running sum is O(n^2).
