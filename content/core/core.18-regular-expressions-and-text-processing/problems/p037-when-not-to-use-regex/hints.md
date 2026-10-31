## Hint 1

For each proposal, imagine the **real** data, not the example in your head. What other ways can
the same HTML link or JSON value be written? Which inputs does `^\(.*\)$` accept that are not
balanced?

## Hint 2

For part 2, think about what you would do by hand to check `((a)(b))`: you would keep a running
count. Can a pattern with a fixed number of pieces hold a number that can grow forever?

```
for each proposal: problem + breaking input + replacement
   a -> html.parser   b -> json.loads   c -> counter / stack
   d -> str.split     e -> str.endswith / pathlib suffix
rule: regex for flat token patterns; parsers for formats; str methods for simple cases
```
