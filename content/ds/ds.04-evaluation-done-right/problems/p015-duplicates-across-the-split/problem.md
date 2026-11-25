# Duplicates across the split

Chapter section 5. Before trusting a test score, check whether test rows also appear (as exact copies) in the training set. A model scores those rows from memory.

Write `cross_split_duplicates(train, test, cols)` returning `(count, ids)`:

- `count`: how many **test** rows are equal, on all of `cols`, to at least one training row
- `ids`: the sorted list of the **index labels** of those test rows

## Example

```text
train rows (a, b): (1, x), (2, y), (2, y)
test  rows (a, b): index 7 -> (2, y),  index 8 -> (3, z),  index 9 -> (1, x)
-> (2, [7, 9])
```
