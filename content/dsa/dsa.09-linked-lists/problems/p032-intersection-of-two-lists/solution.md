## Approach

Let `a` have `x` nodes before the shared part, `b` have `y`, and the shared part `z` nodes. Pointer `p` walks `a` and then `b`, pointer `q` walks `b` and then `a`. To reach the first shared node the second time round, `p` walks `x + z + y` steps and `q` walks `y + z + x` steps: the same number. So they arrive there together. If nothing is shared, both reach `None` together after `x + y` steps (plus the switch), and `p is q` is true with both `None`, which is the right answer.

## Code

```python
def get_intersection(a, b):
    p, q = a, b
    while p is not q:
        p = p.next if p is not None else b       # at the end, switch to the other list
        q = q.next if q is not None else a
    return p                                     # the shared node, or None
```

The loop always ends: each pointer switches lists at most once, so after at most `x + y + z + 2` steps both are on the shared node or both are `None`.

## Complexity

`O(n + m)` time, `O(1)` extra memory.

## Another way

Count both lengths, move the pointer on the longer list ahead by the difference, then walk both together until `p is q`. Same complexity and perhaps easier to explain; the switching trick does the "length difference" automatically. With a set of the nodes of `a` (`O(n)` memory) you can check each node of `b`: simple, but the memory test rejects it here.
