## Hint 1

Start with the small functions and test each by hand. `to_gray`: what shape does `(H, W, 3) @ (3,)` give? `adjust`: why must you convert to `float` *before* the arithmetic (Ch. 4, Ch. 20.3)? `flip`: which slice reverses the columns, and what makes it a copy?

## Hint 2

`blur3`: pad the image by one pixel with `mode="edge"`, then add the 9 shifted views `padded[dy:dy + H, dx:dx + W]` for `dy, dx` in `0, 1, 2`. Why must the sum be a float (or int) array, not `uint8`? `equalise`: `np.bincount`, `cumsum`, then use the 256-entry table as a lookup with fancy indexing, `lut[img]`. What happens to the division when every pixel has the same level?

## Hint 3

```text
to_gray:  check ndim == 3 and shape[2] == 3;  round(img.astype(float) @ [0.299, 0.587, 0.114]).astype(uint8)
adjust:   clip(round((img.astype(float) - 128) * contrast + 128 + brightness), 0, 255).astype(uint8)
flip:     img[:, ::-1].copy() | img[::-1].copy() | else ValueError
blur3:    p = pad(img.astype(float), 1, mode="edge"); total = sum of the 9 shifted (H, W) slices of p
          round(total / 9).astype(uint8)
equalise: counts, cdf, first; if cdf[-1] == first: copy; lut = ...; return lut[img]
pipeline: out = img.copy(); for step in steps: out = step(out); return out
```
