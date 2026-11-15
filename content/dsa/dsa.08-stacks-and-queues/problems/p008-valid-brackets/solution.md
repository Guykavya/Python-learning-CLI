## Approach

Push every opener. A closer must match the top of the stack (the most recent unclosed opener); pop it and compare. Three failures: a closer with an empty stack, a closer that does not match the top, and openers left at the end.

## Code

```python
PAIRS = {")": "(", "]": "[", "}": "{"}


def is_valid(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack
```

## Complexity

`O(n)` time, one pass with `O(1)` work per character. `O(n)` memory in the worst case (all openers).

## Another way

A popular trick pushes the **expected closer** instead of the opener:

```python
def is_valid(text):
    want = {"(": ")", "[": "]", "{": "}"}
    stack = []
    for ch in text:
        if ch in want:
            stack.append(want[ch])
        elif ch in ")]}":
            if not stack or stack.pop() != ch:
                return False
    return not stack
```

The comparison then is simply `stack.pop() != ch`. Both versions do the same work.
