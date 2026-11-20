## Hint 1

Every palindrome has a centre: a letter (odd length) or the gap between two letters (even length). How many centres does a string of length `n` have? From each centre, every successful step outward (`s[lo] == s[hi]`) is **one more** palindrome. Try `"aaa"` on paper: centre at index 1 succeeds twice (`"a"`, then `"aaa"`).

## Hint 2

The table version: `is_pal[i][j]` is True when `s[i] == s[j]` and the inside is a palindrome, where "the inside" is empty or one letter when `j - i < 2`. Fill it so that `is_pal[i + 1][j - 1]` is ready first: by length, or `i` from `n - 1` down to 0. Count the True cells.

## Hint 3

```
total = 0
for centre in 0 .. n-1:
    for (lo, hi) in [(centre, centre), (centre, centre + 1)]:
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            total += 1
            lo -= 1; hi += 1
return total
```
