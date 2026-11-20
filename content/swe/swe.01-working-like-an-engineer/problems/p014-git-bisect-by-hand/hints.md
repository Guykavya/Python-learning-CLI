## Hint 1

If you test the commit in the middle, what do you learn? What is left to search, whichever answer you get?

## Hint 2

Keep two indexes: `lo`, a commit known to be good, and `hi`, a commit known to be bad. The answer is always somewhere after `lo` and at or before `hi`. When are you finished?

## Hint 3

```text
lo = 0; hi = n - 1
while hi - lo > 1:
    mid = (lo + hi) // 2
    if is_bad(commits[mid]): hi = mid
    else: lo = mid
return commits[hi]
```
