## Hint 1

Take `"aaac"` (three `a`s) and write down, by hand, every way `(a+)+` can cover the `a`s:
`aaa`, `aa|a`, `a|aa`, `a|a|a`. How many did you get for 3? For 4? What is the pattern?

## Hint 2

The engine stops at the **first success**. When can it not stop early? Then think: is there
any string that `(a+)+b` matches but `a+b` does not?

```
ways(n) = 2 ** (n - 1)        # each of the n-1 gaps: cut or not
time(n + 2) ≈ 4 * time(n)     # matches the table
fix: a+b, or (?>a+)+b / (a++)+b on 3.11+
```
