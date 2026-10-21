## Approach

Two indexes walk the two lines. Each step takes the smaller front number, so the output grows
in order. This is the "merge" step of merge sort, which you will meet in the DSA track.

## Code

```python
a = input().split()
b = input().split()
if not all(int(x) <= int(y) for x, y in zip(a, a[1:])):
    print("Line 1 is not sorted")
elif not all(int(x) <= int(y) for x, y in zip(b, b[1:])):
    print("Line 2 is not sorted")
else:
    i = 0
    j = 0
    out = ""
    while i < len(a) and j < len(b):
        if int(a[i]) <= int(b[j]):
            out += a[i] + " "
            i += 1
        else:
            out += b[j] + " "
            j += 1
    while i < len(a):
        out += a[i] + " "
        i += 1
    while j < len(b):
        out += b[j] + " "
        j += 1
    print(out.strip() if out else "(empty)")
    print(f"From line 1: {len(a)}, from line 2: {len(b)}")
```

## Why `while` here and not `for`

Each step moves **one** of two positions, and which one depends on the data. A `for` loop
moves one position by one every time. This is a real case where `while` is the right tool.

## Why `<=` takes from line 1 on ties

It keeps equal numbers in their original line order (a property called *stability*), which
matters when the numbers are keys of bigger records.

## Cost

Every step adds one number, so the loop runs `len(a) + len(b)` times. Sorting everything again
would cost more.
