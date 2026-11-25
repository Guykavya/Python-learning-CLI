## Hint 1

Do the colour in two steps: first the "linearised" channels (the gamma correction of the formula), then the weighted sum. For the ratio, which of the two luminances goes on top?

## Hint 2

```text
rgb = to_rgb(hex)
lin = where(rgb <= 0.03928, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
L = 0.2126*lin[0] + 0.7152*lin[1] + 0.0722*lin[2]
ratio = (max(La, Lb) + 0.05) / (min(La, Lb) + 0.05)
```
