## Approach

The same scan as "valid brackets", but every stack entry is `(bracket, index)`. A closer is checked against the top **before** popping, so we can report the closer's own index for the two immediate errors. At the end, the bottom of the stack is the opener that has waited longest: the earliest unclosed one.

## Code

```python
PAIRS = {")": "(", "]": "[", "}": "{"}


def bracket_error(text):
    stack = []                                  # (bracket, index)
    for i, ch in enumerate(text):
        if ch in "([{":
            stack.append((ch, i))
        elif ch in PAIRS:
            if not stack:
                return (i, "unexpected")
            if stack[-1][0] != PAIRS[ch]:
                return (i, "mismatch")
            stack.pop()
    if stack:
        return (stack[0][1], "unclosed")
    return (-1, "ok")
```

## Complexity

`O(n)` time and `O(n)` memory, like the plain check.

## Another way

Some editors report the **innermost** unclosed bracket instead (`stack[-1]`), because that is the one the cursor is usually closest to. For `"((("` that would be index 2 instead of 0; for `"{}(("` it would be index 3 instead of 2. Both are reasonable designs; this problem asks for the earliest.
