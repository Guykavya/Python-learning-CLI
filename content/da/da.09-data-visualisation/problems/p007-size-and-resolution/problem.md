# Size and resolution

Chapter section 3. The size of a picture in pixels is `figsize x dpi`. A 4 x 3 inch figure saved at 50 dpi is 200 x 150 pixels.
Vector formats (SVG) have no pixels at all.

Write `save_png(fig, path, dpi=100)`:

- saves the figure to `path` and returns `path` as a `pathlib.Path`;
- a `.png` file is saved at the given `dpi`; a `.svg` file is saved as SVG (the `dpi` does not matter);
- any other suffix raises `ValueError` with the text `unsupported format`;
- do **not** use `bbox_inches="tight"`: it changes the pixel size.

## Example

```python
fig, ax = plt.subplots(figsize=(4, 3))
save_png(fig, "chart.png", dpi=50)       # a 200 x 150 pixel image
```
