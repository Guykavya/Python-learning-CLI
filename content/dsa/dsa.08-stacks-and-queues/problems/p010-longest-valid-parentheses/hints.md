## Hint 1

Start with `stack = [-1]`. Push the index of every `(`. At a `)`, pop. If the stack is now empty, this `)` cannot be part of any run: push its index as the new "wall". Otherwise, what is the length of the valid run that ends at `i`?

## Hint 2

The run ending at `i` starts at `stack[-1] + 1` and has length `i - stack[-1]`. Remember the best `(start, length)` and only replace it when the new length is **strictly** greater.

```
if not stack: stack.append(i)
else:
    length = i - stack[-1]
    if length > best_len: best_len, best_start = length, stack[-1] + 1
return s[best_start:best_start + best_len]
```
