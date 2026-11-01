## Approach

Count strong references per object after each statement. A weak reference never counts. With
the automatic collector disabled, an object dies exactly when its count reaches zero, or, for a
cycle, when `gc.collect()` is called.

## Trace

| Line | Strong references at that moment | Output |
|---|---|---|
| 1 | Node a: name `b` (the name `a` was deleted) | `1 alive a` |
| 2 | `b` now names a new Node, so Node a has 0 | `2 dead True` |
| 3 | Node c: two list slots (`del c` removed the name) | `3 alive 2` |
| 4 | one list slot | `4 alive` |
| 5 | none | `5 dead` |
| 6 | Node d: the dict value | `6 alive` |
| 7 | the value was replaced by a string | `7 dead` |
| 8 | the local of `make` disappeared with its frame | `8 dead` |
| 9 | Node kept: the name `kept` (the tuple was unpacked, the frame is gone) | `9 alive kept` |
| 10 | `kept = None` | `10 dead` |
| 11 | Node x: `y.other`; Node y: name `y` and `x.other` | `11 alive alive` |
| 12 | x and y hold each other, nothing else holds them: a cycle | `12 alive alive` |
| 13 | `gc.collect()` finds the unreachable cycle and frees both | `13 dead dead True` |

```
1 alive a
2 dead True
3 alive 2
4 alive
5 dead
6 alive
7 dead
8 dead
9 alive kept
10 dead
11 alive alive
12 alive alive
13 dead dead True
```

Notice `rk().name` on line 9: calling the weak reference creates a temporary strong reference
for the duration of the expression, which is dropped again right after, so line 10 still prints
`dead`. If you store `obj = rk()` in a variable, *that* variable keeps the object alive.

## Another way

Add `weakref.finalize(obj, print, "freed", name)` for each object: the message is printed at the
exact moment the object dies, between the numbered lines. That shows the same timeline without
any `state()` calls. Remove `gc.disable()` and the cycle may be freed earlier or later, depending
on when the collector's allocation counter crosses its threshold; that uncertainty is why code must
never rely on *when* cyclic garbage is freed.
