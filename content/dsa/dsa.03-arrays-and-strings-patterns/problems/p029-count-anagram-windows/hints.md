## Hint 1

All windows have the same length `m = len(pattern)`. When the window moves one step to the right, how many
characters change? What does that mean for the letter counts of the window?

## Hint 2

Keep a list `have` of 26 counts for the current window and a list `need` for the pattern. Each step adds the
entering character `text[r]` and removes the leaving one `text[r - m]`. Compare `have == need` only once the
window is full (`r >= m - 1`). Comparing two lists of 26 numbers is O(26), not O(m).

## Hint 3

```
need = counts of pattern; have = 26 zeros; count = 0
for r in 0..n-1:
    have[text[r]] += 1
    if r >= m: have[text[r - m]] -= 1
    if r >= m - 1 and have == need: count += 1
print count
```
