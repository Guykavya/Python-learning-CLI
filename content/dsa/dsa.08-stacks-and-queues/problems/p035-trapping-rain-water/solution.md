## Approach

Think in horizontal layers. A bar that is higher than the top of the stack closes a pool on the right. The popped bar is the floor of a layer; the next bar in the stack is the left wall. The layer is as wide as the gap between the walls and as deep as the lower wall minus the floor. Popping again handles the next, higher layer.

## Code

```python
def trap(height):
    stack = []                                # indices, heights not increasing
    water = 0
    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            bottom = stack.pop()
            if not stack:
                break                         # no left wall
            left = stack[-1]
            width = i - left - 1
            depth = min(height[left], h) - height[bottom]
            water += width * depth
        stack.append(i)
    return water
```

## Complexity

`O(n)` time (each index pushed and popped once), `O(n)` memory.

## Another way

Two pointers with `O(1)` memory (dsa.03): keep `left_max` and `right_max`. Move the pointer on the side with the **lower** maximum, because that side's water level is decided by its own maximum.

```python
def trap(height):
    i, j = 0, len(height) - 1
    left_max = right_max = water = 0
    while i < j:
        if height[i] < height[j]:
            left_max = max(left_max, height[i])
            water += left_max - height[i]
            i += 1
        else:
            right_max = max(right_max, height[j])
            water += right_max - height[j]
            j -= 1
    return water
```
