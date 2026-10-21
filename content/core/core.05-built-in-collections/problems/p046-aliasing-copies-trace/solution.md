## Walkthrough

After the first four lines there are three outer lists: one shared by `a` and `b`, one for
`c`, and one for `d`. The inner list `[2, 3]` is shared by `a`/`b` and `c`; `d` has its own copy.

| Step | Effect |
|---|---|
| `b[0] = 100` | changes the list shared by `a` and `b` |
| `c[1].append(5)` | changes the inner list shared by `a`, `b` and `c` |
| `c[2] = 400` | replaces a slot in `c` only |
| `d[1].append(6)` | changes `d`'s own inner list |

So `a` and `b` print `[100, [2, 3, 5], 4]`, `c` prints `[1, [2, 3, 5], 400]` and `d` prints
`[1, [2, 3, 6], 4]`. Identity: `a is b` is True, `a is c` False, `a[1] is c[1]` True,
`a[1] is d[1]` False.

`e = list(a)` is another shallow copy. Then `a[1] = [9]` **replaces** slot 1 of `a` only, so
`e[1]` still refers to the old inner list `[2, 3, 5]`.

`a += [7]` extends the shared list: `b` now has 4 items; `c` still has 3. `a = a + [8]` builds
a new 5-item list and moves only `a`, so `b` stays at 4.
