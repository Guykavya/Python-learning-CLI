# Reading a p-value correctly

Chapter section 14.2. A p-value is a statement about **how surprising the data are if nothing is going on**. The program computes an exact permutation p-value by listing every way to split 8 numbers into two groups of 4.

```python
from itertools import combinations


def exact_p(a, b):
    pooled = a + b
    obs = abs(sum(a) / len(a) - sum(b) / len(b))
    total = 0
    extreme = 0
    for idx in combinations(range(len(pooled)), len(a)):
        ga = [pooled[i] for i in idx]
        gb = [pooled[i] for i in range(len(pooled)) if i not in idx]
        diff = abs(sum(ga) / len(ga) - sum(gb) / len(gb))
        total += 1
        extreme += diff >= obs - 1e-9
    return obs, extreme, total


obs, extreme, total = exact_p([12, 13, 14, 15], [8, 9, 10, 11])
p = extreme / total
print(f"observed difference {obs:.1f}")
print(f"{extreme} of {total} splits are at least this extreme")
print(f"p = {p:.3f}")
print(f"reject at 0.05: {p < 0.05}")
print(f"reject at 0.01: {p < 0.01}")
_, e, t = exact_p([12, 13, 14], [8, 9, 10])
print(f"3 against 3: smallest possible p = {e / t:.3f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

If only 1 of 20 splits were this extreme, `p` would print as `0.050`.

## After you answer

- Does `p = 0.029` say that the chance the groups are the same is 2.9%? What does it say?
- Why can the 3-against-3 test never reach 0.05?
