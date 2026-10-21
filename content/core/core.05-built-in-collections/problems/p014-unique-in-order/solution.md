## Approach

A set answers `in` in O(1) on average, and a list keeps the order. Use both: the set for the
check, the list for the output.

## Code

```python
n = int(input())
seen = set()
order = []
for _ in range(n):
    name = input().strip()
    if name not in seen:
        seen.add(name)
        order.append(name)
print("Unique:", len(order))
for name in order:
    print(name)
```

## Complexity

O(n). With `if name not in order:` on the list, each check scans the list, making it O(n²):
for 100,000 distinct names that is about five billion comparisons.

## Another way

```python
unique = list(dict.fromkeys(names))
```

Dict keys are unique and keep insertion order, so this keeps the first copy of each name.
