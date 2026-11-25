# Colour maps that deceive

Chapter section 6.9. A good **sequential** colour map gets steadily lighter, or steadily darker, from one end to the other. A rainbow map (`jet`) goes light - dark - light, so two
values far apart can look equally bright and the bright band looks like a **boundary in the data**.

We can test this with numbers. The **luminance** of a colour is `0.2126 R + 0.7152 G + 0.0722 B`. Write:

- `luminance_profile(name, n=64)`: the luminance of `n` colours sampled evenly along the matplotlib colour map `name` (a NumPy array; use `matplotlib.colormaps[name]`
  and the RGB columns only, no alpha);
- `is_monotone_lightness(name)`: `True` when the profile has **no change of direction** (it never goes from rising to falling or the other way; use the signs of the differences
  between neighbours);
- `pick_sequential(names)`: the **first** name in the list that is monotone, or `None` if none is.

This check is for **sequential** maps. A diverging map such as `RdBu` changes direction once on purpose, at its centre.

## Example

`is_monotone_lightness("viridis")` is `True`; `is_monotone_lightness("jet")` is `False`. `pick_sequential(["jet", "viridis", "Blues"])` is `"viridis"`.
