## Approach

Both slow parts are membership tests on lists: `x in b` and `x not in result`. A list answers
"is x in here?" by comparing with each item (O(length)). A set uses the hash of `x` to jump
straight to the right slot (O(1) on average).

- Build `set(b)` **once**: O(len(b)).
- Keep the answer in a list (for the order) **and** a set `seen` (for fast "already added?").

## Code

```python
def common_items(a, b):
    in_b = set(b)
    seen = set()
    result = []
    for x in a:
        if x in in_b and x not in seen:
            seen.add(x)
            result.append(x)
    return result
```

## Complexity

O(len(a) + len(b)) time on average, O(len(b) + len(result)) extra memory. The old version was
O(len(a) · (len(b) + len(result))). With 100,000 items each that is the difference between
well under a second and many minutes.

## Another way

`dict.fromkeys` keeps the first-seen order and removes duplicates in one step:

```python
def common_items(a, b):
    in_b = set(b)
    return list(dict.fromkeys(x for x in a if x in in_b))
```

`set(a) & set(b)` finds the common items quickly but loses the order of `a`; putting it back
with `sorted(..., key=a.index)` brings the quadratic scan straight back.
