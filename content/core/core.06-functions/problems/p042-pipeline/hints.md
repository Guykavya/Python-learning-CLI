## Hint 1

Keep one 'current value' and replace it with `step(current)` for each step.

## Hint 2

```
history = [value]
for step in steps:
    value = step(value)
    history.append(value)
return history if collect else value
```
