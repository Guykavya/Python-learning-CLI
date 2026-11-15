## Hint 1

Keep `current` (the text of the group you are inside) and `k` (the number being read). At `[`, push `(current, k)` and start a fresh `current = ""`, `k = 0`. What should happen at `]`?

## Hint 2

At `]`: pop `(outer, times)` and set `current = outer + current * times`. Digits build the number: `k = k * 10 + int(ch)`.

```
for ch in s:
    digit -> k = k * 10 + int(ch)
    "["   -> push (current, k); current, k = "", 0
    "]"   -> outer, times = pop(); current = outer + current * times
    else  -> current += ch
return current
```
