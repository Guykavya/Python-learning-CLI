## Approach

Every function follows the rule of Ch. 20.10: take a `uint8` array, compute in a wider type, return a new `uint8` array. Then a pipeline is just a list of functions applied in order, and each piece can be tested alone.

- **`to_gray`** is a matrix product on the last axis: `(H, W, 3) @ (3,)` → `(H, W)`. Converting to float first avoids `uint8` overflow, and `np.round` (not `astype` alone, which truncates) gives the nearest level.
- **`adjust`** widens to float, applies the formula, rounds, clips to 0..255, and only then narrows to `uint8`: the clip is what stops `250 + 10` from wrapping to 4.
- **`flip`** is slicing with step −1; slicing gives a view (Ch. 6), so `.copy()` makes it independent.
- **`blur3`** loops over the 9 kernel positions, not the pixels: each shifted slice of the edge-padded image is the whole picture moved by one pixel, and their sum divided by 9 is the 3 × 3 mean everywhere at once (Ch. 20.7).
- **`equalise`** builds the 256-entry lookup table from the cumulative histogram and applies it with one fancy-indexing operation, `lut[img]` (Ch. 20.8). The constant image is the case a first draft gets wrong (division by zero).
- **`pipeline`** copies once at the start, so even an empty list returns a new array.

## Code

```python
import numpy as np

WEIGHTS = np.array([0.299, 0.587, 0.114])


def to_gray(img):
    img = np.asarray(img)
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError(f"expected a colour image of shape (H, W, 3), got {img.shape}")
    return np.round(img.astype(float) @ WEIGHTS).astype(np.uint8)


def adjust(img, brightness=0, contrast=1.0):
    out = (np.asarray(img).astype(float) - 128.0) * contrast + 128.0 + brightness
    return np.clip(np.round(out), 0, 255).astype(np.uint8)


def flip(img, how):
    img = np.asarray(img)
    if how == "horizontal":
        return img[:, ::-1].copy()
    if how == "vertical":
        return img[::-1].copy()
    raise ValueError(f"how must be 'horizontal' or 'vertical', got {how!r}")


def blur3(img):
    img = np.asarray(img)
    if img.ndim != 2:
        raise ValueError(f"blur3 expects a grey (H, W) image, got shape {img.shape}")
    h, w = img.shape
    padded = np.pad(img.astype(float), 1, mode="edge")
    total = np.zeros((h, w))
    for dy in range(3):
        for dx in range(3):
            total += padded[dy:dy + h, dx:dx + w]
    return np.round(total / 9).astype(np.uint8)


def equalise(img):
    img = np.asarray(img)
    counts = np.bincount(img.ravel(), minlength=256)
    cdf = counts.cumsum()
    first = cdf[counts > 0][0]
    if cdf[-1] == first:
        return img.copy()
    lut = np.clip(np.round((cdf - first) / (cdf[-1] - first) * 255), 0, 255).astype(np.uint8)
    return lut[img]


def pipeline(img, steps):
    out = np.asarray(img).copy()
    for step in steps:
        out = step(out)
    return out
```

## Complexity

Each function is O(H × W) time (`blur3` does 9 passes, `equalise` one histogram and one lookup) and allocates a few arrays of the image's size. Nothing loops over pixels in Python.

## Another way

`blur3` with `sliding_window_view(padded, (3, 3)).mean(axis=(2, 3))` (Ch. 20.7) gives the same blur from a view of all 3 × 3 windows; it reads nine times as much memory, so the shifted-slices version is usually lighter. `flip` could use `np.fliplr` / `np.flipud` (views too, so still `.copy()`). In the pipeline, `functools.reduce(lambda acc, step: step(acc), steps, img.copy())` is the same loop in one expression.
