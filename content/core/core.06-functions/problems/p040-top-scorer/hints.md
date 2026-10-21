## Hint 1

Looping over a dict gives its keys. What should the key function return for a name?

## Hint 2

`max(scores, key=lambda name: scores[name])` returns the first name with the top score in dict order, not alphabetical order. How can a tuple key fix ties?

## Hint 3

Use `min` with the key `(-score, name)`: the smallest tuple has the highest score and, on ties,
the alphabetically first name.
```
if not scores: return None
return min(scores, key=lambda name: (-scores[name], name))
```
