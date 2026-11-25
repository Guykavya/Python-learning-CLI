## Walk-through

- p = 0.9: `-ln(0.9) = 0.10536` -> `0.105`
- p = 0.5: `-ln(0.5) = 0.69315` -> `0.693`
- p = 0.1: `-ln(0.1) = 2.30259` -> `2.303`
- p = 0.0: clipped to `1e-15`; `-ln(1e-15) = 15 * 2.30259 = 34.539` -> `34.539`

Mean = (0.10536 + 0.69315 + 2.30259 + 34.53878) / 4 = 37.63988 / 4 = 9.40997 -> `9.410`.

## What it shows

One confidently wrong prediction (it said 0 for a real positive) outweighs the three reasonable ones: the average is 9.41. Log-loss punishes overconfidence severely. The clip only stops it from being infinite.
