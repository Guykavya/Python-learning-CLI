## Approach

Create the range, test for an empty range with truthiness, then print its items and `len`.

## Code

```python
start = int(input())
stop = int(input())
step = int(input())
if step == 0:
    print("step cannot be 0")
else:
    r = range(start, stop, step)
    if r:
        line = ""
        for n in r:
            line += str(n) + " "
        print(line.strip())
    else:
        print("(empty)")
    print(f"Count: {len(r)}")
```

## Why the step-0 check comes first

`range(1, 5, 0)` raises `ValueError` the moment it is created. Guard it before.

## Another way

`print(" ".join(str(n) for n in r))` builds the line in one call. You will use `join` with
generator expressions a lot from the next chapter on.
