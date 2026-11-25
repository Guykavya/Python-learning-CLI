## Model answer

Reply to the manager: the p-value tells us that a difference of exactly zero is very unlikely given the data. It does **not** tell us
that the difference is big or useful. With two million customers per group, almost any difference, however tiny, becomes
statistically detectable, so "significant" is nearly guaranteed here.

What matters first is the **effect size**: the lift is 0.02 percentage points (10.00% to 10.02%). I would report it with its confidence
interval, which will be very narrow around that small number, and compare it with the **minimum effect of interest** we should have
agreed before the test (say 0.5 points). The whole interval is far below that, so the verdict is "real, but not worth it".

What is missing is the **cost-benefit**: 0.02 points of conversion times our monthly checkouts times the value of an order, against two
engineering weeks and a slightly slower page (which may cost conversions elsewhere). My recommendation: do not ship for revenue reasons
unless that arithmetic is clearly positive; keep the result as a learning, and test a bolder change.

**Checklist: your answer should mention**
- [ ] effect size first (0.02 points)
- [ ] the confidence interval
- [ ] the minimum effect of interest
- [ ] the cost of the change against the value of the lift
- [ ] significant is not the same as important
