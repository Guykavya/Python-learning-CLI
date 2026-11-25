# Colour-blind safe pairs

Chapter section 8.2. About 1 man in 12 cannot tell some reds and greens apart. We can **simulate** red-green colour blindness with a matrix and measure how far apart two colours stay.
`simulate` and `separation` are in `starter.py` (given; do not change them):

```python
DEUTAN = np.array([[0.625, 0.375, 0.0], [0.700, 0.300, 0.0], [0.0, 0.300, 0.700]])

def simulate(hex_color):
    return np.clip(DEUTAN @ np.array(matplotlib.colors.to_rgb(hex_color)), 0, 1)

def separation(c1, c2, simulated=True):
    a = simulate(c1) if simulated else np.array(matplotlib.colors.to_rgb(c1))
    b = simulate(c2) if simulated else np.array(matplotlib.colors.to_rgb(c2))
    return float(np.linalg.norm(a - b))
```

Write `safe_pairs(palette, min_sep)`. `palette` is a list of hex colours. Return the list of **all pairs** `(palette[i], palette[j])` with `i < j`, in that
order of `i` then `j`, whose **simulated** separation (`simulated=True`) is **at least** `min_sep`.

## Example

For `["#d62728", "#2ca02c", "#E69F00", "#0072B2"]` and `min_sep = 0.5`, the red/green pair (separation 0.43 with red-green blindness) is **not** returned; orange/blue (1.03) is.
