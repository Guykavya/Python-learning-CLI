## Hint 1

Keep `a, b, c` = `T(i)`, `T(i + 1)`, `T(i + 2)`, starting with `i = 0`: `0, 1, 1`. One step moves the window by one: the new triple is `T(i + 1), T(i + 2), T(i + 3)`. How many steps take `i` from 0 to `n`, and which of the three variables is then `T(n)`?

## Hint 2

Use one tuple assignment, so the right side is computed from the **old** values before anything changes (chapter section 6, rolling variables).

```
a, b, c = 0, 1, 1
repeat n times:
    a, b, c = b, c, a + b + c
return a
```
