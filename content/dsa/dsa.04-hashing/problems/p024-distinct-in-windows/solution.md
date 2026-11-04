## Approach

A sliding window with a dictionary of counts. `len(count)` is the number of distinct values only if keys with count 0
are **deleted**, so delete them.

## Code

```python
n, k = map(int, input().split())
a = [int(x) for x in input().split()]

count = {}
for x in a[:k]:
    count[x] = count.get(x, 0) + 1
answer = [len(count)]

for i in range(k, n):
    x = a[i]
    count[x] = count.get(x, 0) + 1
    old = a[i - k]
    count[old] -= 1
    if count[old] == 0:
        del count[old]
    answer.append(len(count))

print(*answer)
```

## Complexity

O(n) time on average and O(k) memory.

## Another way

`len(set(a[i:i+k]))` for every `i` is a one-liner that is O(n * k): 4 * 10^10 steps in the worst case of this problem.

## Order of the two updates

Adding the new element first and removing the old one second is safe even when they are equal: the count goes from
1 to 2 and back to 1, and the key never disappears by mistake.
