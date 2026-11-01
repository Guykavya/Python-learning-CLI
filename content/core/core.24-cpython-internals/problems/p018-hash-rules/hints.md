## Hint 1

- `check_hashable`: is there a better test than looking at the type? What does `hash()` do when
  something inside a tuple is unhashable?
- `Point`: which two methods must agree with each other? Which tuple could you hash? How do you
  block `p.x = 5` while still letting `__init__` store `x`?
- `lost_keys`: iteration walks the stored entries; `in` computes the hash *now*. How can you use
  that difference?
- `hash_collisions`: a dict from hash to a list of values builds the groups. When should a new
  value *not* be added to its group?

## Hint 2

```
check_hashable(obj):  try hash(obj) -> True; except TypeError -> False

class Point:
    __slots__ = ("x", "y")
    __init__: object.__setattr__(self, "x", x) ... (bypasses your own __setattr__)
    __setattr__: raise AttributeError
    __eq__: compare (x, y) tuples
    __hash__: return hash((self.x, self.y))

lost_keys(d) = [k for k in d if k not in d]

hash_collisions(values):
    groups = {}
    for v in values:
        g = groups.setdefault(hash(v), [])
        if no item in g == v: g.append(v)
    return [g for g in groups.values() if len(g) >= 2]
```
