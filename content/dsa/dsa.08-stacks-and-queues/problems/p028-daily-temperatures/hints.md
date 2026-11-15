## Hint 1

Keep a stack of **day indices** still waiting for a warmer day. When day `i` arrives with temperature `t`, which waiting days does it answer, and what is each one's distance?

## Hint 2

```
wait = [0] * len(temps)
for i, t in enumerate(temps):
    while stack and temps[stack[-1]] < t:
        j = stack.pop(); wait[j] = i - j
    stack.append(i)
```
