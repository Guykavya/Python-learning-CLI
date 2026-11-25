## Hint 1

What does each rule function return, and which rows do you want: the `True` or the `False` ones? How do you turn the
Series into "the rows that fail", and how do you read their **labels** (not positions)? What should happen to a missing
value in the answer of a rule?

## Hint 2

```text
result = []
for name, rule in rules.items():
    ok = rule(df).fillna(True).astype(bool)
    bad = ~ok
    if bad.any():
        result.append((name, int(bad.sum()), df.index[bad.to_numpy()][:3].tolist()))
return result
```
