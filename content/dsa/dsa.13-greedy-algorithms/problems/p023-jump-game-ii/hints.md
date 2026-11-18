## Hint 1

Do not decide where to land. Instead ask: with `jumps` jumps, how far right can I be at most? Call it `layer_end`. While you scan the indices up to `layer_end`, keep `farthest = max(i + nums[i])`: the end of the next layer.

## Hint 2

When `i` reaches `layer_end`, you must jump to go any further: `jumps += 1`, and the new layer ends at `farthest`. Stop the loop **before** the last index: you never need to jump *from* the last index (chapter section 16, trap 11).

## Hint 3

```
jumps = 0; layer_end = 0; farthest = 0
for i in range(len(nums) - 1):
    farthest = max(farthest, i + nums[i])
    if i == layer_end:
        jumps += 1
        layer_end = farthest
return jumps
```
