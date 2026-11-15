## Approach

Push every character, then pop until the stack is empty. The stack gives the characters back in the reverse order of arrival (LIFO), so collecting them in pop order is the reversed string. Building a list and joining once at the end avoids the `O(n^2)` cost of `out = out + ch` on very long strings.

## Code

```python
def reverse_string(s):
    stack = []
    for ch in s:
        stack.append(ch)          # push
    out = []
    while stack:                  # an empty list is falsy
        out.append(stack.pop())   # pop: the newest character first
    return "".join(out)
```

## Complexity

`O(n)` time: every character is pushed once and popped once, and `append`/`pop` at the end of a list are `O(1)`. `O(n)` extra memory for the stack and the output list.

## Another way

In real code you write `s[::-1]`, which does the same in one step and is faster because it runs in C. The stack version matters because the same pattern (push now, take back in reverse later) is how undo, the call stack and bracket matching work.
