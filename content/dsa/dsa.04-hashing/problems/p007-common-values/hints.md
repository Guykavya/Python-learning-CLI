## Hint 1

If you had the values of A in a structure with O(1) membership, how would you test each value of B?

## Hint 2

`set(a)` gives the distinct values of A. The intersection with `set(b)` keeps values in both. Then sort it.

## Hint 3

```
common = set(a) & set(b)
print(len(common))
print(*sorted(common))
```
