## Hint 1

`p` is a period exactly when `s[:n - p] == s[p:]`: the string shifted by `p` matches itself. That says that the prefix of length `n - p` is also a suffix, so it is a **border**. Periods and borders come in pairs: `p = n - b`.

## Hint 2

The longest border is `b = pi[n - 1]`, so the smallest period is `n - pi[n - 1]`. The next border is the longest border of that border, `pi[b - 1]`, and so on down to 0 (chapter section 11, "All borders").

## Hint 3

```
pi = prefix_function(s)
periods = []
b = pi[-1]
while b > 0:
    periods.append(n - b); b = pi[b - 1]
periods.append(n)              # border 0 gives the period n
return periods                 # already increasing
```
