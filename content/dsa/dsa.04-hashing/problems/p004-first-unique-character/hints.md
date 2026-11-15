## Hint 1

After one full pass you know how many times each letter occurs. What second pass finds the first letter whose count is 1?

## Hint 2

Pass 1: build `count`. Pass 2: `for i, ch in enumerate(s)` and return the first `i` with `count[ch] == 1`.

## Hint 3

```
count = {}
for ch in s: count[ch] = count.get(ch, 0) + 1
for i, ch in enumerate(s):
    if count[ch] == 1: print(i); stop
print(-1)
```
