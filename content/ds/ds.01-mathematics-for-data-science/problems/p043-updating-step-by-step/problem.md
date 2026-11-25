# Updating step by step

Chapter section 10.4. After one test you know more than before, so the **posterior becomes the next prior**. A positive result is evidence for the disease; a **negative** result is evidence against it, with `P(sick | -) = (1 - sens) * prior / ((1 - sens) * prior + (1 - fpr) * (1 - prior))`.

Write `sequential_posterior(prior, results, sensitivity=0.99, false_positive_rate=0.05)` where `results` is a list of booleans (`True` = positive). Apply the updates in order and return the final probability of being sick. An empty list returns the prior. Assume the tests are independent given the true state.

## Example

```text
sequential_posterior(0.01, [True])          ->  0.1667
sequential_posterior(0.01, [True, True])    ->  0.7984   (about)
sequential_posterior(0.01, [True, False])   ->  small again
```
