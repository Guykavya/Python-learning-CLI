## Approach

Build the dict, then swap each pair with a dict comprehension. Duplicate values collide in the
inverted dict, and the later assignment wins, while the key keeps the position of its first
insertion.

## Code

```python
colours = {}
for _ in range(int(input())):
    key, value = input().split()
    colours[key] = value
inverted = {v: k for k, v in colours.items()}
for v, k in inverted.items():
    print(f"{v} -> {k}")
```

## Complexity

O(n) to build and O(n) to invert.

## Note

Inverting is only lossless when the values are unique. To keep **all** keys for a value, invert
into a dict of lists with `setdefault`.
