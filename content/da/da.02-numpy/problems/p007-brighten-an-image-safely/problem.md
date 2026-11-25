# Brighten an image safely

Chapter sections 4.2 and 20.3. Image pixels are `uint8` (0 to 255). Write `add_clipped(img, delta)` that adds the
whole number `delta` (between −255 and 255) to every pixel and **clips** the result to 0..255:

- 250 + 10 must give 255, not 4 (no wrap-round);
- 5 − 10 must give 0, not 251;
- the result is a **new** `uint8` array of the same shape (grey `(h, w)` or colour `(h, w, 3)`);
- the input image is not changed.

No Python loops.

## Example

```python
img = np.array([[250, 100, 5]], dtype=np.uint8)
add_clipped(img, 10).tolist()    # [[255, 110, 15]]
add_clipped(img, -10).tolist()   # [[240, 90, 0]]
add_clipped(img, 10).dtype       # dtype('uint8')
```
