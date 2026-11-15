## Hint 1

When you meet a closer, which opener must it match: the first one you saw, or the most recent one that is still open? Which structure gives you "the most recent one" in `O(1)`?

## Hint 2

```
PAIRS = {")": "(", "]": "[", "}": "{"}
for ch in text:
    if ch in "([{": push ch
    elif ch in PAIRS:
        if stack is empty or stack.pop() != PAIRS[ch]: return False
return stack is empty
```
