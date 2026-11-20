## Hint 1

Find every component as in p016, but keep the list of vertices each search visits. Which component do you keep when a new one has the **same** size as the best so far?

## Hint 2

```
best = []
for s in range(n):
    if seen[s]: continue
    comp = vertices reached by a search from s (mark them seen)
    if len(comp) > len(best): best = comp          # strictly greater keeps the earlier one on a tie
return sorted(best)
```
