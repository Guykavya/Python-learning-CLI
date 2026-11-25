## Model answer

1. For the **degree-10 polynomial** (high variance): with ten times more data the training error rises slightly (it can no longer pass through every point), the validation error falls substantially, and the **gap narrows**. More data pin down the many coefficients, so the curve stops following the noise. (In the chapter's table a degree-12 model's validation RMSE falls from 78.9 at 12 rows to 0.31 at 320 rows.)
2. For the **straight line** (high bias): both errors stay high and converge to the same poor level (about 0.5 against a noise floor of 0.3). The best straight line through a sine is a fixed line; more data estimate it more precisely but cannot make it bend. The learning curve **plateaus** with a small gap.
3. **Bias** is the systematic error of a model that is too simple for the truth; more data do not reduce it. **Variance** is how much the fitted model changes between training samples; more data reduce it.
4. Give the second team a **more flexible model** (a higher-degree polynomial, a spline, extra features) and check the learning curve again. Collecting data for a model that has already plateaued is wasted effort.

**Checklist: your answer should mention**
- [ ] variance falls as the number of rows grows
- [ ] bias does not fall with more data
- [ ] for the flexible model the gap between validation and training error shrinks
- [ ] for the straight line the learning curve plateaus at a high error
- [ ] more capacity or better features is the remedy for high bias
