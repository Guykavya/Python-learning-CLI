## Hint 1

Let `a` have `x` private nodes, `b` have `y` private nodes, and both share `z` nodes. If you knew `x` and `y`, how far would you move the pointer on the longer list before walking both together?

## Hint 2

Without counting: `p` walks `a` and, when it falls off the end, continues at the head of `b`; `q` does the opposite. After `x + z + y` steps both have walked the same distance. Where are they then? And if nothing is shared (`z = 0`)?

## Hint 3

```
p, q = a, b
while p is not q:
    p = p.next if p is not None else b
    q = q.next if q is not None else a
return p
```
