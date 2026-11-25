# Expected calibration error

Chapter section 11.2. The **expected calibration error** (ECE) summarises a reliability table in one number: the average gap between observed and predicted rate, weighted by how many rows each bin holds.

```text
ECE = sum over non-empty bins of  |observed - predicted| * n_bin / N
```

Write `ece(y, p, bins=10)` with the **equal-width** bins of the previous problem (`k = min(floor(p * bins), bins - 1)`), returning a float.

## Example

```text
y = [0, 0, 1, 1, 1];  p = [0.05, 0.15, 0.12, 0.95, 0.91]
ece(y, p, 10)  ->  (0.05 * 1 + 0.365 * 2 + 0.07 * 2) / 5 = 0.184
```
A perfectly calibrated model has an ECE near 0; probabilities squashed towards 0.5 have a large ECE even when their ranking (AUC) is perfect.
