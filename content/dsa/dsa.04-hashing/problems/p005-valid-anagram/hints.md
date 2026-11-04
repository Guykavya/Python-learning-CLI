## Hint 1

What single number can you compare first that rules out many pairs at once?

## Hint 2

Count the characters of `s` in a dictionary, then walk through `t` and subtract. If a count would go below 0, or lengths differ, the answer is `NO`.

## Hint 3

```
if len(s) != len(t): NO
count = {}
for ch in s: count[ch] += 1
for ch in t: count[ch] -= 1 (missing -> NO)
all counts must be 0
```
