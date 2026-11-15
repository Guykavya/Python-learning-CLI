## Hint 1

Build the deque in one line: `deque(ch.lower() for ch in text if ch.isalnum())`. What should happen when it holds 0 or 1 characters?

## Hint 2

```
while len(d) > 1:
    left = d.popleft(); right = d.pop()
    if left != right: return (left, right)
return None
```
