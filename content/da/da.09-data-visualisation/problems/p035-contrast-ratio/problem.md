# Contrast ratio

Chapter section 8.2. Text and thin lines must stand out from their background. The WCAG guideline measures this with the **contrast ratio** of two colours, at least
**4.5** for normal text and **3** for large text and graphics.

1. `rel_luminance(hex_color)`: convert the colour to RGB values between 0 and 1 (`matplotlib.colors.to_rgb` does it), then make each channel linear:
   `c / 12.92` if `c <= 0.03928`, otherwise `((c + 0.055) / 1.055) ** 2.4`. The relative luminance is `0.2126 R + 0.7152 G + 0.0722 B` of the linear channels.
2. `contrast_ratio(fg, bg="#ffffff")`: with `a` and `b` the two luminances, `(max + 0.05) / (min + 0.05)`.
3. `passes_aa(fg, bg="#ffffff", large=False)`: `True` when the contrast ratio is at least 4.5 (at least 3 when `large=True`).

```python
contrast_ratio("#000000")        # 21.0
contrast_ratio("#777777")        # about 4.48: a light grey that just fails AA
```

## Example

Black on white: luminances 0 and 1, so `(1 + 0.05) / (0 + 0.05) = 21`. A colour against itself gives 1.
