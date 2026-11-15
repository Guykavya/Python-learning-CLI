## Hint 1

In `1 2 3 4 5`, which two elements trade places first? After that swap, which part is still unreversed?

## Hint 2

Turn `l` and `r` into 0-based indices `i = l - 1`, `j = r - 1`. Swap, then `i += 1`, `j -= 1`. Keep going
while `i < j`. When the part has odd length, the middle element stays where it is.

## Hint 3

```
for each operation l r:
    i, j = l - 1, r - 1
    while i < j:
        a[i], a[j] = a[j], a[i]
        i += 1
        j -= 1
print a
```
