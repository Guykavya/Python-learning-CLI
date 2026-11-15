## Hint 1

Sort the candidates so that equal values sit next to each other. Each position may be used once: after choosing position `i`, the next call starts at `i + 1`.

## Hint 2

At one level of the loop, trying the value 1 a second time (from another position) builds exactly the same sub-trees as the first time. Skip it: `if i > start and candidates[i] == candidates[i - 1]: continue`.

## Hint 3

```
def go(start, remaining):
    if remaining == 0: record a copy; return
    for i in range(start, len(c)):
        if c[i] > remaining: break
        if i > start and c[i] == c[i - 1]: continue
        path.append(c[i]); go(i + 1, remaining - c[i]); path.pop()
```
