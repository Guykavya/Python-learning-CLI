## Hint 1

At most 3 attempts: a `for` loop over `range` fits. What should happen as soon as the PIN is right?

## Hint 2

The number of tries left after attempt 1, 2, 3 is 2, 1, 0. Can a `range` count down like that?

## Hint 3

```
for left in range(2, -1, -1):
    if input().strip() == pin: print Welcome; break
    if left > 0: print tries left (try/tries)
    else: print Card blocked
```
