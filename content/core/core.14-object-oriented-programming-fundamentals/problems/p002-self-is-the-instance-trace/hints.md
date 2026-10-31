## Hint 1

Keep a small table with one row per **object** (not per name): `a` starts at 0, `b` at 10. Each
call adds to the row of the object before the dot. When you reach `c = a`, do you add a new row,
or does `c` share a row with `a`?

## Hint 2

Rewrite each call in the long form `Counter.method(obj, ...)` and update your table:

```
a.tick()          -> Counter.tick(a)       a: 0 -> 1
a.tick(5)         -> Counter.tick(a, 5)    a: 1 -> 6
print(b.tick())   -> b: 10 -> 11, prints the returned 11
c.tick(100)       -> c is a, so a: 6 -> 106
Counter.tick(b, 2) -> b: 11 -> 13
b.reset()          -> b: 0
r()                -> r remembers a, so a.tick()
```
