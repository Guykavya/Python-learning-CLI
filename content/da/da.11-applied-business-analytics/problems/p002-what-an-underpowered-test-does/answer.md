## Model answer

With too few visitors the estimate of the lift is **noisy**: one run says +1.4 points, the next +0.1, the next -0.2. A real effect of +0.7 points sits in the middle of that wide spread, so many runs end up
with an interval that includes zero and the test "finds nothing": the effect was real but the test had **low power** and **missed** it most of the time.

The runs that do reach significance are the ones whose estimate landed far to the right, by luck. Averaged over only those runs, the lift comes out well above the truth: significant results from small tests are
**exaggerated** (the "winner's curse").

The same spread puts some estimates **below zero**: a small test can show a harmful banner that is actually helpful. A significant result with the wrong **sign** is possible when power is low.

Before starting, decide the smallest effect worth detecting (here +0.5 points, the lift at which the banner pays for itself), compute the visitors per group with `n_per_group` (about 36,800), run the test for that
long and no shorter, and judge the result by its **interval**, not only by a p-value.

**Checklist: your answer should mention**
- [ ] low power: the estimates are spread out, so a real effect is often missed
- [ ] the significant runs are the lucky large ones, so the lift is exaggerated
- [ ] some runs get the sign wrong
- [ ] plan the sample size from the smallest effect worth detecting, before the test
- [ ] judge by the interval, and do not stop early
