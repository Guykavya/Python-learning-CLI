## Hint 1

Solve `n = 2` by hand: where must the small disc go so that the big one can move to `target`?

## Hint 2

Three steps: move `n - 1` discs from `source` to `spare` (using `target` as the helper), move disc `n` from `source` to `target`, move the `n - 1` discs from `spare` to `target` (using `source` as the helper).

## Hint 3

```
if n == 0: return []
return (hanoi(n - 1, source, spare, target)
        + [(source, target)]
        + hanoi(n - 1, spare, target, source))
```
