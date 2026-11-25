## Model answer

1. **R-squared 0.866**: the share of the variation in scores that the line explains; here hours explain about 87% of the score variance (the rest is noise around the line).
2. **Prob (F-statistic) 9.22e-14**: the probability of seeing a fit this good if the model were no better than a flat line at the mean; it is tiny, so the model as a whole is clearly better than nothing.
3. **coef of x1 = 5.29**: the estimated change in score for one extra hour of study; each extra hour goes with about 5.3 more points.
4. **std err of x1 = 0.393**: how much the slope estimate would wobble from sample to sample; the interval 4.49 to 6.09 is about two standard errors either side of 5.29.
5. **t of x1 = 13.5**: the coefficient divided by its standard error, i.e. how many standard errors the slope is away from zero; 13 is very far.
6. **P>|t| of x1 = 0.000**: the probability of a t this extreme if the true slope were 0; below 0.0005 here, so a zero slope is not believable.
7. **Durbin-Watson 2.01**: compares neighbouring residuals; values near 2 mean no first-order correlation in the residuals (meaningful only if the row order matters).
8. **Jarque-Bera 0.651 (Prob 0.722)**: tests whether skew and kurtosis of the residuals look normal; the large p-value gives no evidence against normal residuals.

**Checklist: your answer should mention**
- [ ] R-squared is the share of variance explained, not "accuracy"
- [ ] the F p-value compares the whole model with an intercept-only model
- [ ] the coefficient is the change in `y` per one unit of `x`, with the unit stated
- [ ] the standard error measures sampling uncertainty of the estimate
- [ ] t = coefficient / standard error
- [ ] the p-value is computed assuming the true slope is zero (not the chance that it is zero)
- [ ] Durbin-Watson near 2 means no residual autocorrelation
- [ ] Jarque-Bera checks normality of residuals through skew and kurtosis
