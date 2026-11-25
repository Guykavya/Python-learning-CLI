## Hint 1

`np.lexsort((k1, k2, k3))` sorts by `k3` first, breaks ties with `k2`, then with `k1` (Ch. 15.2). Which of your three keys is the most important, and where must it go in the tuple?

## Hint 2

`lexsort` always sorts **ascending**. How do you make "higher score first" ascending for a number? (You cannot negate a string, but you do not need to: names are ascending.)

## Hint 3

```text
names  = asarray(names, dtype=str)
scores = asarray(scores, dtype=float)
ages   = asarray(ages)
return lexsort((names, ages, -scores))     # last key = primary
```
