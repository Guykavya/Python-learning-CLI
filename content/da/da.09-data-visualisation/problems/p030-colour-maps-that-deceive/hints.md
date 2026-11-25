## Hint 1

First get the 64 RGB colours from the map, then turn each into one number with the luminance formula. A direction change is a place where the difference to the next value changes sign.

## Hint 2

```text
rgb = matplotlib.colormaps[name](np.linspace(0, 1, n))[:, :3]
lum = rgb @ [0.2126, 0.7152, 0.0722]
d = np.diff(lum)
changes = number of i with sign(d[i+1]) != sign(d[i])
```
