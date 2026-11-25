## Approach

Count the true positives and the false positives as shares of the population; the posterior is the share of true positives among all positives.

## Code

```python
def bayes_posterior(prior, sensitivity, false_positive_rate):
    tp = sensitivity * prior
    fp = false_positive_rate * (1 - prior)
    if tp + fp == 0:
        raise ValueError("no one can test positive: the posterior is undefined")
    return tp / (tp + fp)
```

## Complexity

O(1).

## Another way

Think in natural frequencies: 10,000 people give 99 sick-and-positive and 495 healthy-and-positive (the next problem).
