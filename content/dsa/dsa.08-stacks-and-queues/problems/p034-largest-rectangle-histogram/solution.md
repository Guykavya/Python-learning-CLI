## Approach

For each bar, the widest rectangle of its height is bounded by the nearest smaller bar on each side. In an increasing stack, the element below any index is its previous smaller (or equal) bar, and the bar that pops it is its next smaller (or equal) bar. So at the moment of the pop we know both boundaries and can compute the area. The extra `0` at the end pops every bar that is left.

## Code

```python
def largest_rectangle(heights):
    stack = []                               # indices, heights increasing
    best = 0
    for i, h in enumerate(heights + [0]):    # the final 0 forces everything to be popped
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1
            width = i - left - 1
            best = max(best, height * width)
        stack.append(i)
    return best
```

## Complexity

`O(n)` time (each index pushed and popped once) and `O(n)` memory.

## Another way

Compute two arrays first with two monotonic-stack passes: `left[i]`, the index of the previous strictly smaller bar, and `right[i]`, the index of the next strictly smaller bar. Then the answer is `max(heights[i] * (right[i] - left[i] - 1))`. Same complexity; easier to debug because you can print both arrays.

With equal bars, popping on `>=` can give a too-short width for the first of them, but the **last** equal bar to be popped gets the full width, so the maximum is still right.
