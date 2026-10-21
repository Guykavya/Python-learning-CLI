# Quick stats with built-ins

Read one line of whole numbers separated by spaces. Print:

```
Count: 5
Sum: 12
Min: -3
Max: 9
Spread: 12
```

`Spread` is max minus min. If the line has no numbers, print:

```
Count: 0
Sum: 0
Min: none
Max: none
```

(no `Spread` line).

Use `sum()`, `min()` and `max()`, and use `default=` for the empty case instead of an `if`
around the `min`/`max` calls. The tests check that you call all three built-ins.
