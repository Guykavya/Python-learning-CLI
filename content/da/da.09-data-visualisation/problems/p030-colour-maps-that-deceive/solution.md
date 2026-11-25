## Approach

A monotone map has all differences of the same sign. The number of sign changes of the differences is the number of times the lightness turns around: 0 for viridis, 1 for jet.

## Code

```python
import matplotlib
import numpy as np


def luminance_profile(name, n=64):
    rgb = matplotlib.colormaps[name](np.linspace(0, 1, n))[:, :3]
    return rgb @ np.array([0.2126, 0.7152, 0.0722])


def is_monotone_lightness(name):
    d = np.diff(luminance_profile(name))
    changes = int(np.sum(np.sign(d[1:]) != np.sign(d[:-1])))
    return changes == 0


def pick_sequential(names):
    for name in names:
        if is_monotone_lightness(name):
            return name
    return None
```

## Complexity

O(n) per map.

## Another way

Convert to the CIELAB colour space and look at the L* channel; it models human lightness better than this linear formula, but the answer is the same for these maps.
