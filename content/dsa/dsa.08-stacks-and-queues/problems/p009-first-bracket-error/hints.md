## Hint 1

You need two facts about every open bracket: its kind and its position. What can you push so that the stack remembers both?

## Hint 2

The earliest unclosed opener is the one that was pushed first and never popped: the **bottom** of the stack, `stack[0]`.

```
for i, ch in enumerate(text):
    if opener: push (ch, i)
    elif closer:
        if stack empty: return (i, "unexpected")
        if stack[-1][0] != PAIRS[ch]: return (i, "mismatch")
        pop
return (stack[0][1], "unclosed") if stack else (-1, "ok")
```
