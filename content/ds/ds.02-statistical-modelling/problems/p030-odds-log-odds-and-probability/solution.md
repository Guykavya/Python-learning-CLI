## Walk-through

- p = 0.2: odds = 0.2 / 0.8 = 0.250; log-odds = ln(0.25) = -1.386; back = 0.200.
- p = 0.5: odds = 1.000; log-odds = ln(1) = 0.000; back = 0.500.
- p = 0.8: odds = 0.8 / 0.2 = 4.000; log-odds = ln(4) = 1.386; back = 0.800.

The log-odds of 0.2 and 0.8 are equal in size and opposite in sign: swapping "success" and "failure" flips the sign of the log-odds. That symmetry is a reason log-odds are the natural scale for a linear model.

## Another way

`scipy.special.logit` and `expit` do the two conversions.
