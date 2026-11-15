## Hint 1

Keep indices with heights that do not increase from bottom to top. When `h` is higher than the top, pop the top: it is the **bottom** of a pool. If the stack is now empty there is no left wall and the water runs away. Otherwise, what are the width and depth of the layer?

## Hint 2

```
while stack and height[stack[-1]] < h:
    bottom = stack.pop()
    if not stack: break
    left = stack[-1]
    width = i - left - 1
    depth = min(height[left], h) - height[bottom]
    water += width * depth
stack.append(i)
```
