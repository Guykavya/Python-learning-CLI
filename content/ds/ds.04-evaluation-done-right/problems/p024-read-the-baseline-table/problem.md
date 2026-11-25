# Read the baseline table

Chapter section 8. Three methods were scored on the **same five cross-validation folds** (ROC-AUC per fold). Because the folds are shared, compare them **pair by pair**: take the fold-by-fold differences, their mean, and the standard error of that mean. A rough rule: call one method better only if the mean difference is more than **two standard errors** above zero.

```python
import math

rule = [0.70, 0.68, 0.72, 0.69, 0.71]
logit = [0.76, 0.73, 0.78, 0.74, 0.77]
boost = [0.77, 0.72, 0.79, 0.73, 0.76]


def compare(a, b):
    d = [x - y for x, y in zip(a, b)]
    mean = sum(d) / len(d)
    sd = math.sqrt(sum((v - mean) ** 2 for v in d) / (len(d) - 1))
    se = sd / math.sqrt(len(d))
    verdict = "better" if mean > 2 * se else "no clear difference"
    return mean, se, verdict


for name, a, b in [("logistic vs rule", logit, rule), ("boosting vs logistic", boost, logit)]:
    mean, se, verdict = compare(a, b)
    print(f"{name}: mean difference {mean:+.3f}, standard error {se:.4f}, {verdict}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

(Values you may use: `sqrt(5) = 2.2361`, `sqrt(30e-6) = 0.005477`, `sqrt(120e-6) = 0.010954`.)

## Example

For `a = [0.8, 0.8]` and `b = [0.7, 0.7]` the differences are `0.1, 0.1`: mean `+0.100`, standard error `0.0000`, `better`.

## After you answer

- Boosting has the highest single fold (0.79). Why is that not evidence that it is better?
