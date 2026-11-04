## Walkthrough

First call, target 8:

| i | x | need | `seen` printed | found? |
|---|---|---|---|---|
| 0 | 4 | 4 | `{}` | no, then store 4 |
| 1 | 9 | -1 | `{4: 0}` | no, then store 9 |
| 2 | 1 | 7 | `{4: 0, 9: 1}` | no |
| 3 | 6 | 2 | `{4: 0, 9: 1, 1: 2}` | no |
| 4 | 5 | 3 | `{4: 0, 9: 1, 1: 2, 6: 3}` | no |
| 5 | 3 | 5 | `{4: 0, 9: 1, 1: 2, 6: 3, 5: 4}` | yes: `seen[5] = 4`, pair `4 5` |

## Output

```
i = 0 x = 4 need = 4 seen = {}
i = 1 x = 9 need = -1 seen = {4: 0}
i = 2 x = 1 need = 7 seen = {4: 0, 9: 1}
i = 3 x = 6 need = 2 seen = {4: 0, 9: 1, 1: 2}
i = 4 x = 5 need = 3 seen = {4: 0, 9: 1, 1: 2, 6: 3}
i = 5 x = 3 need = 5 seen = {4: 0, 9: 1, 1: 2, 6: 3, 5: 4}
pair 4 5
i = 0 x = 3 need = 3 seen = {}
i = 1 x = 3 need = 3 seen = {3: 0}
pair 0 1
i = 0 x = 5 need = 5 seen = {}
no pair
```

## Key ideas

- Each element asks one question: "is my complement already stored?" That replaces the inner loop.
- Check first, then store: otherwise an element could pair with itself (`x = target / 2`).
- Equal values work: the first `3` is stored before the second `3` asks.
- The function does O(n) work: one lookup and one store per element.
