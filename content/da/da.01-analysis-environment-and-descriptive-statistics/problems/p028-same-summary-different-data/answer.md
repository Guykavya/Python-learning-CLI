## Model answer

**What each picture shows.**
- **A** is a roughly bell-shaped *shape*: one pile in the middle, thinning symmetrically. Here the mean and standard deviation describe the data well.
- **B** is *bimodal*: two clusters near 40 and 60 and nothing near 50. The mean of 50 describes a value no one has.
- **C** has 19 values packed together just below 50 and one far-away *outlier* near 93. The standard deviation of 10 is made almost entirely by that one value; the typical spread of the 19 is tiny.
- **D** has a long tail to the right: most values are between 40 and 55, a few reach 70 or 80. The mean is pulled above the median.

**Why the two numbers cannot tell them apart.** The mean is a balance point and the standard deviation an average squared distance. Both are single numbers computed from all values, so completely different arrangements can produce the same pair. Two numbers cannot carry the *shape*.

**Extra numbers that separate them.** The *five-number summary* (min, Q1, median, Q3, max): C has min 47 and a max of 93 with a median near 48 and Q1 to Q3 almost equal; D has a median clearly below the mean; B has Q1 near 40 and Q3 near 60. The **median** exposes C and D (below the mean), the **IQR** exposes C (tiny) and B (wide), and **skewness** exposes C and D (large positive) while A is near 0. Bimodality is the hardest to see in numbers: a histogram shows it, a single statistic does not.

**Before trusting a summary: *plot first*.** Draw a histogram or box plot, look at the five-number summary, check the minimum and maximum for impossible values, and only then quote a mean.

**Averaging averages.** If group A has 10 people with mean 50 and group B has 90 people with mean 60, the overall mean is 59, not 55: the mean of group means ignores group sizes (the trap behind Simpson's paradox).

**Checklist: your answer should mention**
- [ ] a concrete description of each of A, B, C, D (bell, bimodal, one outlier, right tail)
- [ ] that mean and sd are two numbers and cannot capture shape
- [ ] median, quartiles/five-number summary or skewness as separating numbers
- [ ] bimodal data: the mean describes an empty middle, the median does too
- [ ] plot first, then summarise
- [ ] the mean of group means is not the overall mean unless the groups have equal sizes
