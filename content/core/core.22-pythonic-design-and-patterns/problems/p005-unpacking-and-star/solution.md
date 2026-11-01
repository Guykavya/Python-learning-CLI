## Approach

Unpacking gives names to positions. It also checks the shape for free: `x, y, z = p` raises an
error if `p` does not have exactly three items, while `p[0]`, `p[1]`, `p[2]` silently ignore a
fourth.

- `first, *rest = items` needs at least one item, so empty input is handled first.
  `*rest` is **always a list**, whatever the input type.
- `_, *middle, _ = items` needs at least two items, so short input returns `[]` first.
- In `a, b = b, a + b` the right side is fully computed before any name changes, so no
  temporary variable is needed.
- `|` on dicts builds a **new** dict; later dicts win on equal keys.

## Code

```python
def describe_point(p):
    x, y, z = p
    return f"x={x}, y={y}, z={z}"


def split_head_tail(items):
    if not items:
        return None, []
    first, *rest = items
    return first, rest


def trim_ends(items):
    if len(items) < 2:
        return []
    _, *middle, _ = items
    return middle


def swap_pairs(pairs):
    return [(b, a) for a, b in pairs]


def distance_between(segment):
    (x1, y1), (x2, y2) = segment
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def merge_settings(defaults, user, overrides):
    return defaults | user | overrides
```

## Complexity

`fib` is O(n) additions; `swap_pairs` O(n); the rest are O(1) or O(length) because of the copy
into a list. `merge_settings` is O(total keys).

## Another way

`merge_settings` also works as `{**defaults, **user, **overrides}`, which works on Python older
than 3.9. `split_head_tail` can use `head, *tail = items` inside `try/except ValueError`, or
`iter` and `next`. `math.dist(a, b)` computes `distance_between` in the standard library.
