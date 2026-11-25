## Hint 1

The share explained by component `i` is `s[i]**2 / sum(s**2)`. How do you turn a list of shares into running totals?

## Hint 2

```text
share_i = s**2 / sum(s**2)
cum = cumsum(share_i)
return first index where cum >= share, plus 1
```
Beware rounding at 1.0: allow `1e-12`.
