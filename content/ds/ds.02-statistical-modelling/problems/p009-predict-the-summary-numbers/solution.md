## Walk-through

mean_x = 3, mean_y = 4. Centred x: -2, -1, 0, 1, 2. Centred y: -2, 0, 1, 0, 1.

Sxy = (-2)(-2) + (-1)(0) + 0 + 0 + 2 * 1 = 4 + 0 + 0 + 0 + 2 = 6. Sxx = 4 + 1 + 0 + 1 + 4 = 10. Slope = 0.6. Intercept = 4 - 0.6 * 3 = 2.2.

Fitted: 2.8, 3.4, 4.0, 4.6, 5.2. Residuals: -0.8, 0.6, 1.0, -0.6, -0.2. RSS = 0.64 + 0.36 + 1.00 + 0.36 + 0.04 = 2.4. TSS = 4 + 0 + 1 + 0 + 1 = 6. R-squared = 1 - 2.4 / 6 = 0.6.

Residual degrees of freedom = 5 - 2 = 3. The largest absolute residual is 1.00 at x = 3 (the point is above the line).

## Another way

`np.polyfit(x, y, 1)` returns `[0.6, 2.2]`.
