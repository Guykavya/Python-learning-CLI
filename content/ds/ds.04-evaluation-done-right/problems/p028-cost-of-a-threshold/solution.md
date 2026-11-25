## Walk-through

Positives are rows 0, 3, 7 with p = 0.9, 0.35, 0.65.

- t = 0.3: predicted positive: p >= 0.3 is rows 0, 1, 2, 3, 5, 7, 8, 9. Missed positives: none. False positives (y = 0): rows 1, 2, 5, 8, 9 = 5. Cost 5 * 5 = 25.
- t = 0.5: predicted positive: rows 0, 1, 5, 7, 9. Missed: row 3 (0.35). False positives: rows 1, 5, 9 = 3. Cost 15 + 100 = 115.
- t = 0.7: predicted positive: rows 0, 9. Missed: rows 3 and 7. False positives: row 9. Cost 5 + 200 = 205.

Cheapest: 0.3.

## Why so low

A miss costs 20 times more than a false alarm, so it pays to call many people. With calibrated probabilities the best threshold is near `cost_fp / (cost_fp + cost_fn) = 5 / 105 = 0.05`.
