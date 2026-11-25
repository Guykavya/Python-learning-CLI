## Hint 1

Write each pair as two rows, right-aligned, padding with 1s on the left. For `(5, 1, 4)` and `(3, 1)`:

```text
5 1 4
1 3 1
```

Now compare column by column. Which columns are equal, which have a 1, and is there any column with two different numbers neither of which is 1?

## Hint 2

```text
for each pair:
    pad the shorter shape with 1s on the left
    for each axis: if a == b -> a;  elif a == 1 -> b;  elif b == 1 -> a;  else -> error
    print the tuple of results, or "error"
```

Careful with `(4, 3) + (4,)`: the `(4,)` lines up with the **last** axis (3), not the first.
