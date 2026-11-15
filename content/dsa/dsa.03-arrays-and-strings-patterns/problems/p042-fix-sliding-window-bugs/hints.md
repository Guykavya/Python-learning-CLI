## Hint 1

Run the starter on `aaaa` with `k = 1` by hand. When `left = 0` and `right = 3`, how many characters are in the window?
What does the program use as the length? Then look at `aabbcc`, `k = 2`: after `a` leaves the window completely,
print `count`. Is `a` still a key?

## Hint 2

Take `eceba`, `k = 2`. At `right = 3` the window is `eceb` (three distinct). Remove one character from the left:
`e`. Is `ceb` a good window? The line `total += right - left + 1` assumes the window is good at that moment.

## Hint 3

The three one-line fixes, in pseudocode:

```
while len(count) > k:          # not `if`: keep shrinking until the window is good
    out = s[left]
    count[out] -= 1
    if count[out] == 0:        # the character left the window completely
        delete count[out]
    left += 1
best = max(best, right - left + 1)
```
