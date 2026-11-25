# Bayes for a medical test

Chapter section 10.2. A test for a disease has a **sensitivity** (chance of a positive test if you are sick) and a **false positive rate** (chance of a positive test if you are healthy). Given a positive result, the probability of being sick is

`P(sick | +) = sens * prior / (sens * prior + fpr * (1 - prior))`.

Write `bayes_posterior(prior, sensitivity, false_positive_rate)`. If the denominator is 0 (nobody can test positive) raise `ValueError`.

## Example

```text
bayes_posterior(0.01, 0.99, 0.05)  ->  0.1667     (a positive test: only 1 in 6 are sick)
bayes_posterior(0.0, 0.99, 0.05)   ->  0.0
```
