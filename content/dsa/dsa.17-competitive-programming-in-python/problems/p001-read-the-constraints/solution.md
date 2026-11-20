## Approach

Compute the budget `10**7 * s`, compute the seven costs in table order, and remember the last class whose cost fits. `2 ** n` is only computed when `n <= 60`; a larger `n` makes it far bigger than any budget.

```python
import math
import sys

NAMES = ["log n", "n", "n log n", "n sqrt n", "n^2", "n^3", "2^n"]


def main():
    data = sys.stdin.read().split()
    t = int(data[0])
    out = []
    for i in range(t):
        n = int(data[1 + 2 * i])
        s = int(data[2 + 2 * i])
        budget = 10**7 * s
        costs = [
            math.log2(n),
            n,
            n * math.log2(n),
            n * math.sqrt(n),
            n * n,
            n**3,
            2**n if n <= 60 else math.inf,
        ]
        best = 0
        for k, c in enumerate(costs):
            if c <= budget:
                best = k
        out.append(NAMES[best])
    print("\n".join(out))


main()
```

Example: `n = 10**6`, `s = 1`: the budget is `10**7`; `n log n` is about `2 * 10**7`, which is **over**, so only `n` (and `log n`) fit, and the answer is `n`. With three seconds the budget is `3 * 10**7` and `n log n` fits.

## Complexity

`O(t)`: seven multiplications per case.

## Another way

Keep the classes in a list of `(name, function)` pairs, and stop reading the table at the first class that does not fit **only if** you know the costs are increasing. They are for large `n`, but not for tiny `n`, so the "take the last that fits" loop is the safe version.
