## Model answer

**The promise.** If you draw `n` independent values from a distribution with mean `mu` and finite variance `sigma^2` (the exponential qualifies), then for large `n` the **sample mean** has a distribution that is close to a **normal** bell curve, centred on `mu`, with standard deviation `sigma / sqrt(n)` (the **standard error**). Repeat the experiment many times and a histogram of the averages looks like a bell, even though a single draw is very skewed. The bigger `n` is, the closer to normal; with a very skewed distribution such as the exponential you need a few dozen draws, with a symmetric one a handful.

**What it does not promise.** The data themselves do **not** become normal. A histogram of the individual waiting times stays skewed, with its long right tail, however many you collect. The theorem is about the **average** (and sums), not about the individual values. It also does not save you if the variance is infinite, or if the draws are strongly dependent.

**Why `sigma / sqrt(n)`.** The variance of a sum of independent values is the sum of the variances: `n sigma^2`. Dividing the sum by `n` to get the mean divides the variance by `n^2`, leaving `sigma^2 / n`, so the standard deviation is `sigma / sqrt(n)`. The error shrinks with the **square root** of the sample size: to halve the error you need **four times** as many observations, and to get ten times more precise a hundred times more.

**Checklist: your answer should mention**
- [ ] the sample mean (not the data) is approximately normal for large `n`
- [ ] centred on the true mean, with spread `sigma / sqrt(n)`
- [ ] the raw data stay skewed: the theorem is about the mean
- [ ] variances add, so the standard error falls as `1 / sqrt(n)` (four times the data to halve it)
