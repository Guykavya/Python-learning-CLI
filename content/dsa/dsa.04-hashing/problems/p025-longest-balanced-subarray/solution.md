## Approach

After the substitution the problem is "longest subarray with sum 0". For each running total store only the **first**
index it occurred. The longer the block, the earlier it should start, so the first occurrence is the best.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

first = {0: -1}
s = 0
best = 0
for i, x in enumerate(a):
    s += 1 if x == 1 else -1
    if s in first:
        best = max(best, i - first[s])
    else:
        first[s] = i
print(best)
```

## Complexity

O(n) time and O(n) memory.

## Another way

Brute force over all `(l, r)` pairs with running counts is O(n^2). The prefix dictionary is the usual trick for "longest
subarray with a property that can be written as a sum".
