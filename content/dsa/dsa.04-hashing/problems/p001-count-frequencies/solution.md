## Approach

Walk through the list once. For every value `x`, look up its current count (0 if it is new) and store the count plus 1.
Python dictionaries remember the order in which keys were first added, so iterating over `count.items()` prints the
values in first-appearance order.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

count = {}
for x in a:
    count[x] = count.get(x, 0) + 1

for value, c in count.items():
    print(value, c)
```

## Complexity

O(n) time on average: one lookup and one store per element, each O(1) on average. O(d) memory for `d` distinct values.

## Another way

`collections.Counter(a)` does the same counting in one call, and it also keeps first-appearance order for ties and
printing. The slow way is `a.count(x)` for every distinct `x`: each call scans the whole list, so it is O(n * d).
