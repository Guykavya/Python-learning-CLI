## Hint 1

Read the report from the bottom up: which test is named in the `FAILED` line, and what is `joined` compared with in the line starting `E   assert`? What would
`joined == items` mean if the function lost the last piece? Then ask what shrinking is for: why would a maintainer prefer `[0]` to a list of fifty numbers?

## Hint 2

Evaluate `range(0, len(items) - size, size)` by hand for `items=[0], size=1` and then for `items=[0], size=3`. Does the result depend on `size`? Also try `items=[]`:
does the property fail there?

```
chunk([0], 1):   range(0, 1 - 1, 1) = range(0, 0)  -> empty -> []
chunk([0], 3):   range(0, 1 - 3, 3) = range(0, -2) -> empty -> []
chunk([], 1):    range(0, 0 - 1, 1) -> empty -> []   and [] == [] holds
fix: pieces start at every index below len(items)
```
