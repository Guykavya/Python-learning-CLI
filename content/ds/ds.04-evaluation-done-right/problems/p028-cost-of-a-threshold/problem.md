# Cost of a threshold

Chapter section 10. A threshold turns probabilities into decisions. With a cost for each kind of error you can **price** every threshold. Here a false positive (an unnecessary call) costs 5 and a false negative (a missed churner) costs 100.

```python
y = [1, 0, 0, 1, 0, 0, 0, 1, 0, 0]
p = [0.9, 0.6, 0.4, 0.35, 0.2, 0.55, 0.1, 0.65, 0.3, 0.8]
COST = {"fp": 5, "fn": 100}


def total_cost(t):
    fp = sum(1 for yi, pi in zip(y, p) if pi >= t and yi == 0)
    fn = sum(1 for yi, pi in zip(y, p) if pi < t and yi == 1)
    return fp * COST["fp"] + fn * COST["fn"]


costs = {}
for t in [0.3, 0.5, 0.7]:
    costs[t] = total_cost(t)
    print(f"threshold {t}: cost {costs[t]}")
print(f"cheapest: {min(costs, key=costs.get)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

At threshold 1.0 nobody is predicted positive: the 3 positives are all missed, cost `300`.

## After you answer

- Why is the cheapest threshold so low (much lower than 0.5)?
