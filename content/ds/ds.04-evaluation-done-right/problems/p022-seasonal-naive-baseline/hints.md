## Hint 1

Which values make up the last full season? How does `i % season` let you repeat them for a horizon longer than a season?

## Hint 2

```text
t = asarray(train, float); if len(t) < season: raise ValueError
last = t[-season:]
return array([last[i % season] for i in range(horizon)])
```
