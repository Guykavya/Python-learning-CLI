## Hint 1

What is the answer for a list that contains only plain values? Now suppose you already know the depth of every inner list: how do you combine them?

## Hint 2

Keep the best depth seen among the inner lists, starting from 0 (no inner lists). The answer is 1 + that best.

## Hint 3

```
best = 0
for item in xs:
    if isinstance(item, list): best = max(best, depth(item))
return 1 + best
```
