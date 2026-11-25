## Approach

Widen, compute, clip, narrow. `int16` holds −510..510 easily, so the sum is exact; `np.clip` brings it back into 0..255; `astype(np.uint8)` returns the image type. Clipping must happen in the wide type: once the `uint8` sum has wrapped, 4 looks like a perfectly valid dark pixel.

## Code

```python
import numpy as np


def add_clipped(img, delta):
    wide = img.astype(np.int16) + delta
    return np.clip(wide, 0, 255).astype(np.uint8)
```

## Complexity

O(number of pixels). Two temporary arrays of `int16` (twice the image size each).

## Another way

A lookup table (Ch. 20.8) is faster for big images: build `lut = np.clip(np.arange(256) + delta, 0, 255).astype(np.uint8)` once (256 entries) and return `lut[img]`. Fancy indexing with the image as the index gives a new array of the same shape.
