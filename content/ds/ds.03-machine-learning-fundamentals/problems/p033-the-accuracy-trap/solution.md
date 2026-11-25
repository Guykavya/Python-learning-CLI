## Walk-through

**always no** `(0, 0, 20, 980)`: accuracy = 980 / 1000 = 0.980. `tp + fp = 0`, so precision = 0.0. `tp + fn = 20`, recall = 0 / 20 = 0.0. `precision + recall = 0`, so F1 = 0.0.

**alarm model** `(15, 25, 5, 955)`: accuracy = (15 + 955) / 1000 = 0.970. Precision = 15 / 40 = 0.375. Recall = 15 / 20 = 0.750. F1 = 2 * 0.375 * 0.75 / (0.375 + 0.75) = 0.5625 / 1.125 = 0.500.

## The lesson

The model that never finds a single case has the **higher accuracy** (98.0% against 97.0%). Only recall and F1 show that the alarm model finds three quarters of the cases. On imbalanced data accuracy rewards doing nothing.
