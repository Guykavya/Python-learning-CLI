## Hint 1

Which Series method flags every value that already appeared earlier? What do you get when you filter a column by that flag and then ask for its distinct values? What should happen if that list is empty?

## Hint 2

```text
dup = df[key][df[key].duplicated()].unique().tolist()
if dup:  raise ValueError("<key> has duplicated keys: <dup>")
return df.set_index(key)
```
Alternative check: `df[key].is_unique` tells you whether to raise, but not which keys to list.
