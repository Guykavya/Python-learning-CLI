# Linear search or binary search?

The list `a` holds the numbers 1 to 100 in order. For each target, the program counts how many elements a
**linear search** looks at, and how many middle elements a **binary search** looks at. Binary search only works
on a sorted list: it looks at the middle, and throws away the half that cannot contain the target.

Predict **exactly** what it prints. Do not run it.

```python
a = list(range(1, 101))          # 1, 2, ..., 100, sorted

for target in [50, 1, 100, 37, 101]:
    linear = 0
    for x in a:
        linear += 1
        if x == target:
            break

    lo = 0
    hi = len(a) - 1
    binary = 0
    found = False
    while lo <= hi:
        mid = (lo + hi) // 2
        binary += 1
        if a[mid] == target:
            found = True
            break
        elif a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    print(target, found, linear, binary)
```

Write your answer in `answer.txt`, one line per target, for example `7 True 7 3`.

Note: `a[mid]` equals `mid + 1` here, because the list starts at 1. For the first target, `mid = (0 + 99) // 2 = 49`
and `a[49] = 50`.

## After you answer

What is the largest number of steps binary search can ever need on a list of 100 elements? On a list of a million?
