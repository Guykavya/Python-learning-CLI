## Hint 1

Forget "exactly" for a moment. If the window `a[left..right]` has at most `m` distinct values, how many subarrays
that **end at `right`** have at most `m` distinct values? (Every shorter piece of a good window is good.)

## Hint 2

`atMost(m)` is one left-to-right pass: add `a[right]` to a count dictionary, shrink from the left with `while` until
there are at most `m` keys (delete a key when its count reaches 0), then add `right - left + 1`. The answer is
`atMost(k) - atMost(k - 1)`. What does `atMost(0)` return? (Every window must be empty, so 0.)

## Hint 3

```
def at_most(m):
    count = {}, left = 0, total = 0
    for right in 0..n-1:
        count[a[right]] += 1
        while number of keys > m:
            remove a[left] from count (delete key at 0)
            left += 1
        total += right - left + 1
    return total

print(at_most(k) - at_most(k - 1))
```
