## Hint 1

Take one element at a time (`key = a[i]`). What do you do with the larger values on its left?

## Hint 2

Walk `j` from `i - 1` down while `j >= 0 and a[j] > key`: copy `a[j]` to `a[j + 1]`, count a shift, decrease `j`. Then `a[j + 1] = key`.

## Hint 3

```
for i in range(1, n):
    key = a[i]; j = i - 1
    while j >= 0 and a[j] > key:
        a[j + 1] = a[j]; shifts += 1; j -= 1
    a[j + 1] = key
```
