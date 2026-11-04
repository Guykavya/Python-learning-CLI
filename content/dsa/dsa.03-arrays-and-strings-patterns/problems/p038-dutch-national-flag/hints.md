## Hint 1

Split the array into four zones: 0s at the front, then 1s, then the part you have not looked at yet, then 2s at the
back. Which three positions mark the borders between those zones?

## Hint 2

Use `low` (end of the 0s), `mid` (the next unknown value) and `high` (start of the 2s, minus one). Look at `a[mid]`:

- 0: swap it with `a[low]`; move `low` and `mid` forward;
- 1: already in place; move `mid` forward;
- 2: swap it with `a[high]`; move `high` back, but **not** `mid`. Why not?

## Hint 3

```
low = mid = 0; high = n - 1
while mid <= high:
    if a[mid] == 0: swap a[low], a[mid]; low += 1; mid += 1
    elif a[mid] == 1: mid += 1
    else: swap a[mid], a[high]; high -= 1
print a
```
