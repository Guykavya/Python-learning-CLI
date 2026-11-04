## Approach

Everything before `w` is the finished, duplicate-free prefix. The fast pointer scans ahead. Because the array is
sorted, a value is new exactly when it differs from the last kept value `a[w - 1]`. The write never overtakes the
read (`w <= r`), so no value is overwritten before it is read.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

w = 0
for r in range(n):
    if w == 0 or a[r] != a[w - 1]:
        a[w] = a[r]
        w += 1

print(w)
print(*a[:w])
```

## Complexity

O(n) time, O(1) extra memory (the list is reused).

## Another way

Build a new list and append `x` when it differs from the last appended value. Same O(n) time, O(n) extra memory.
`list(dict.fromkeys(a))` also keeps first occurrences in order and works on unsorted lists. The slow habits are
`if x not in result` (a scan of `result` for every element, O(n * k)) and `a.pop(i)` in a loop (each pop shifts the
tail, O(n^2)).
