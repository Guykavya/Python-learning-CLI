## Hint 1

Which question does each mean answer? "Average mark with credit weights", "average growth factor per year", "average speed over the same distance twice". Which of the three needs logs, and which needs the *reciprocals*?

## Hint 2

```text
weighted: validate, then sum(v*w for v, w in zip(values, weights)) / sum(weights)
geometric: validate v > 0; math.exp(sum(math.log(v) for v in values) / len(values))
harmonic:  validate v > 0; len(values) / sum(1 / v for v in values)
```
