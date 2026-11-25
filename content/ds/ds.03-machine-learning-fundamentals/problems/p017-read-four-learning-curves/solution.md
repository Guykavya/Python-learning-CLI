## Walk-through

- A: last row (320, 0.05, 0.90): gap 0.85, 0.85 / 0.90 = 0.94 > 0.15: `high variance`.
- B: (320, 0.50, 0.53): gap 0.03, ratio 0.057, not > 0.15; 0.53 > 0.375: `high bias`.
- C: (320, 0.29, 0.31): gap 0.02, ratio 0.065; 0.31 not > 0.375: `fine`.
- D: (320, 0.20, 0.27): gap 0.07, ratio 0.07 / 0.27 = 0.259 > 0.15: `high variance`.

## Curve D

D has a validation error (0.27) **below** the stated floor of 0.30, so the floor is probably wrong, or the data are easier. The rule is only as good as its inputs: check the noise-floor estimate before trusting `high variance`, and look at whether the gap is still shrinking with n.
