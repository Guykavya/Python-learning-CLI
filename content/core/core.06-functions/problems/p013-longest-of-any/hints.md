## Hint 1

What should the 'best so far' start as, so that the no-argument case needs no special code?

## Hint 2

To keep the **first** of equal-length words, replace the best only when a word is **strictly** longer.

## Hint 3

```
best = ""
for w in words:
    if len(w) > len(best):
        best = w
return best
```
