# Image pipeline

This is the module project (Ch. 20): image manipulation with NumPy arrays. An image is a `uint8` array: shape `(H, W)` for grey, `(H, W, 3)` for colour (red, green, blue), values 0 (black) to 255 (full brightness). Write six functions. Every function returns a **new** `uint8` array and never changes its input. No Python loops over pixels (a loop over the 9 positions of a 3 × 3 kernel is fine).

## `to_gray(img)`

Colour `(H, W, 3)` → grey `(H, W)`: the weighted sum `0.299 R + 0.587 G + 0.114 B` per pixel (Ch. 20.2), rounded to the nearest integer (`np.round`), as `uint8`. Raise `ValueError` if `img` is not 3-D with 3 channels.

## `adjust(img, brightness=0, contrast=1.0)`

Any shape. Compute in `float64`: `out = (img - 128) * contrast + 128 + brightness`, round with `np.round`, **clip to 0..255**, then convert to `uint8` (Ch. 20.3). No wrap-around: `250 + 10` must give `255`, never `4`. The identity settings return an equal image.

## `flip(img, how)`

`how = "horizontal"` mirrors left-right, `how = "vertical"` mirrors top-bottom (Ch. 20.4); 2-D or 3-D images. Return a copy, not a view. Any other `how` raises `ValueError`.

## `blur3(img)`

Grey `(H, W)` only. Each pixel becomes the mean of its 3 × 3 neighbourhood, with the image's border pixels repeated outside the edge (`np.pad(..., mode="edge")`, Ch. 20.7), rounded with `np.round`, as `uint8`. Same shape as the input.

## `equalise(img)`

Histogram equalisation with a lookup table (Ch. 20.8), for a grey image:

```text
counts = number of pixels at each level 0..255     (np.bincount(img.ravel(), minlength=256))
cdf    = running total of counts
first  = cdf at the darkest level that occurs
lut    = round((cdf - first) / (cdf[255] - first) * 255), clipped to 0..255, as uint8
result = lut[img]
```

If every pixel has the same level (`cdf[255] == first`), return an unchanged copy. For any other image the result uses the full range: its darkest pixel is 0 and its brightest 255.

## `pipeline(img, steps)`

`steps` is a list of functions that each take one image and return one image. Apply them **in order**, each to the result of the previous one, and return the final image. With no steps, return a **copy** of `img`. Use `lambda` for steps that need arguments: `lambda a: adjust(a, contrast=0.5)`.

## Example

```python
red = np.zeros((2, 2, 3), dtype=np.uint8)
red[..., 0] = 255
to_gray(red)
# array([[76, 76],
#        [76, 76]], dtype=uint8)                0.299 * 255 = 76.245
adjust(np.array([250, 10], dtype=np.uint8), brightness=10)
# array([255,  20], dtype=uint8)                clipped, not wrapped to 4
result = pipeline(scene, [to_gray, lambda a: adjust(a, contrast=0.5), blur3, equalise])
# a (H, W) uint8 image with min 0 and max 255; scene is unchanged
```

The test builds a small synthetic scene in the style of Ch. 20.2 (sky, sun, ground, a building) and checks shapes, dtypes, the formulas, `blur3` against a pixel-by-pixel loop, the full range after `equalise`, and that no input is ever changed.
