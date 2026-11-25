## Model answer

1. The **mean confidence interval** (`mean_ci_lower`, `mean_ci_upper`) says where the *average* price of 1,000 sq ft flats lies: the uncertainty about the position of the regression line at that area. The **prediction interval** (`obs_ci_*`) says where the price of **one new flat** of that area will probably fall: it adds the scatter of individual flats around the line.
2. The buyer's question (my flat) needs the **prediction interval**: about 27.8 to 43.5 lakh at n = 100. The analyst's question (the average) needs the **confidence interval**: 34.85 to 36.42.
3. The **confidence interval** shrank (from about 1.6 wide to 0.15 wide) because the line is estimated more and more precisely, its standard error falls like 1/sqrt(n). The **prediction interval** barely changed (about 15.8 to 15.5 wide) because individual flats keep their own noise (sd about 4 lakh) however well the line is known; it can never shrink below about plus or minus 1.96 times the residual standard deviation.

**Checklist: your answer should mention**
- [ ] the confidence interval is for the mean response (the line), the prediction interval for one new observation
- [ ] the prediction interval adds the residual variance
- [ ] the buyer needs the prediction interval, the analyst the confidence interval
- [ ] the confidence interval shrinks with n
- [ ] the prediction interval does not shrink to zero: the noise sigma does not shrink with n
