## Hint 1

How can you test, for each test row, whether its tuple of values is in a set of training tuples? Which data structure makes that test fast?

## Hint 2

```text
seen = set of tuples from train[cols]
hits = [label for label, row in zip(test.index, tuples of test[cols]) if row in seen]
return len(hits), sorted(hits)
```
