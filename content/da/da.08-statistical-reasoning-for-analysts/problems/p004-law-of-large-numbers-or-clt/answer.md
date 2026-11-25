## Model answer

The **law of large numbers** says that as the sample grows, the sample average settles near the true population mean. The **central
limit theorem** says something about the *shape*: the distribution of the sample mean over many repeated samples becomes close to a
normal curve, centred on the true mean with spread `sigma / sqrt(n)`. One concerns where the average goes, the other how it varies
around that value.

The colleague's sentence is wrong because the CLT does not make *the data* normal. Customer spend stays skewed however many customers
we have; what becomes approximately normal is the distribution of the **sample mean** (what we would see if we repeated the survey).
That is why we can build confidence intervals for a mean even from skewed data.

The CLT depends on the sample size `n`, not on the size of the population (5,000 customers out of 5 million or out of 50,000 matters
little). It works slowly when data are very skewed or have extreme values: a large `n` is then needed before the normal
approximation is good.

**Checklist: your answer should mention**
- [ ] the average settles near the true mean (law of large numbers)
- [ ] the shape of the sampling distribution becomes normal (CLT)
- [ ] the data themselves do not become normal
- [ ] n is the sample size, not the population size
- [ ] skewed data need a larger n
