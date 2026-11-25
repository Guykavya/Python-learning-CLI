## Hint 1

What are the *drawn* heights when the axis does not start at zero? Subtract the bottom of the axis from each bar height before you take the ratio. Compare that ratio with the ratio of the raw heights.

## Hint 2

```text
visual_change: y0 = ylim[0]; h = [height - y0 for each bar]; h[1]/h[0] - 1
lie_factor:    visual_change / (heights[1]/heights[0] - 1)
is_truncated:  no bars -> False; vertical: ylim[0] > 0; horizontal: xlim[0] > 0
```
