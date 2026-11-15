## Approach

A monotonic stack of day indices, with temperatures that never increase from bottom to top. A warmer day pops every colder waiting day at the top; the distance is the difference of the indices. Days still on the stack at the end never see a warmer day and keep `0`.

## Code

```python
def daily_temperatures(temps):
    wait = [0] * len(temps)
    stack = []                                 # indices of days still waiting
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            wait[j] = i - j
        stack.append(i)
    return wait
```

## Complexity

`O(n)` time (each day pushed once, popped at most once), `O(n)` memory. A falling list keeps all days on the stack; a rising list keeps one.

## Another way

Because temperatures are between 30 and 100, you can scan from the **right** and keep `next_day[t]`, the nearest later day with temperature exactly `t`. For each day, look at all warmer temperatures `t + 1 .. 100` and take the nearest. That is `O(71 n)`, also linear, but it depends on the small range; the stack works for any numbers.
