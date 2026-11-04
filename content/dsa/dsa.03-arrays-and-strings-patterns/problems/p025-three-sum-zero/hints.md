## Hint 1

Sort the array first. If you fix the smallest value `a[i]`, you need two values to its right that sum to
`-a[i]`. Which earlier problem in this module finds a pair with a given sum in a sorted array in one pass?

## Hint 2

For each `i`, put `l = i + 1` and `r = n - 1`. If the sum is too small, move `l` right; if it is too big, move
`r` left. When it is zero, record it and move **both**. Duplicates: skip an `i` whose value equals the previous
`a[i]`, and after a match skip `l` past copies of the value you just used.

## Hint 3

```
sort a
for i in 0..n-3:
    if i > 0 and a[i] == a[i-1]: continue
    l, r = i+1, n-1
    while l < r:
        s = a[i] + a[l] + a[r]
        if s < 0: l += 1
        elif s > 0: r -= 1
        else:
            record (a[i], a[l], a[r]); l += 1; r -= 1
            while l < r and a[l] == a[l-1]: l += 1
print count, then the triplets in the order found
```

Because `i` goes up and, for a fixed `i`, `l` goes up, the triplets come out already in the required order.
