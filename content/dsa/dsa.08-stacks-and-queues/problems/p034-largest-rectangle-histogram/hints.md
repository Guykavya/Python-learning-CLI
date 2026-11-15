## Hint 1

Keep a stack of indices with heights increasing from bottom to top. When bar `i` is **lower** than the top, the top bar cannot stretch to the right past `i`. Its left limit is the bar now below it in the stack (or the left edge if the stack becomes empty). What is the width?

## Hint 2

```
for i, h in enumerate(heights + [0]):
    while stack and heights[stack[-1]] >= h:
        height = heights[stack.pop()]
        left = stack[-1] if stack else -1
        best = max(best, height * (i - left - 1))
    stack.append(i)
```

`heights + [0]` builds a new list, so `heights` itself is not changed.
