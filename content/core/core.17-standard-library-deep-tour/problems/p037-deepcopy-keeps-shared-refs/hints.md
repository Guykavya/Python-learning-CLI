## Hint 1

In `box`, the keys `"a"` and `"b"` hold the **same** list. When `deepcopy` reaches `"b"`, it has
already copied that list for `"a"` and stored it in `memo`. So what does `c["b"]` point to? And is
any of the copy shared with `shared`?

## Hint 2

`grid` is one inner list used twice. The deep copy is also one (new) inner list used twice. So
what does writing `g2[0][0]` do to `g2[1]`? For `loop`, the copy's second item is the copy itself.

## Hint 3

For `H`: the second `deepcopy` uses the **same** `memo` dict, where `id(x)` is already a key.
For `J`: the copy of `a` copies `b`, whose `peers` lead back to `a`, which is already in `memo`.
For `K`: `copy.copy` copies only the outer list; `deepcopy` of `[shared, [shared]]` meets `shared`
twice, at two different depths.
