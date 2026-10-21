## Hint 1

Can you split the records into two lists first: those with the field and those without?

## Hint 2

`sorted(have, key=lambda r: r[field], reverse=descending)`. Does `reverse=True` keep equal items in their original order? (Yes: Python's sort stays stable with `reverse`.)

## Hint 3

```
have = [r for r in records if field in r]
missing = [r for r in records if field not in r]
return sorted(have, key=lambda r: r[field], reverse=descending) + missing
```
