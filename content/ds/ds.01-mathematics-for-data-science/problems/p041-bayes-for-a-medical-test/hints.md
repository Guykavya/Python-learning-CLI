## Hint 1

Two kinds of people test positive: the sick ones and the healthy ones. How large is each group relative to the whole population?

## Hint 2

```text
tp = sens * prior                  # sick and positive
fp = fpr * (1 - prior)             # healthy and positive
return tp / (tp + fp)
```
