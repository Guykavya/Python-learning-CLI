## Approach

This is a BFS on the indices, where the layers are intervals. Layer 0 is `[0, 0]`. If layer `j` is `[a, b]`, layer `j + 1` ends at the largest `i + nums[i]` for `i` in `[a, b]`. We only need the end of the current layer (`layer_end`) and the end of the next one (`farthest`). When the scan reaches `layer_end`, one more jump is forced.

```python
def min_jumps(nums):
    jumps = 0
    layer_end = 0          # furthest index reachable with `jumps` jumps
    farthest = 0           # furthest index reachable with `jumps + 1` jumps
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == layer_end:             # must jump now to go further
            jumps += 1
            layer_end = farthest
    return jumps
```

Greedy view: we delay each jump until it is forced, and then we jump to the place that reaches farthest. Any other landing spot reaches no farther, so it cannot need fewer jumps afterwards.

The loop runs to `len(nums) - 2`. If it ran to the last index, in `[1, 1]` it would count a jump *from* the last index: 2 instead of 1.

## Complexity

`O(n)` time, `O(1)` space.

## Another way

A plain BFS from index 0, with a `dist` list and a queue, gives the same answer. It is the obviously-correct version and a good test oracle, but it looks at every index each jump covers: `O(n * max jump)`. You can make it linear by remembering the furthest index already pushed and only pushing indices beyond it, which turns it back into the layer scan above.
