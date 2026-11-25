# Odds, log-odds and probability

Chapter section 13.2. Three ways to say the same thing: probability `p`, odds `p / (1 - p)` and log-odds `ln(odds)`. The sigmoid turns log-odds back into a probability.

```python
import math

for p in [0.2, 0.5, 0.8]:
    odds = p / (1 - p)
    log_odds = math.log(odds)
    back = 1 / (1 + math.exp(-log_odds))
    print(f"p={p}: odds {odds:.3f}, log-odds {log_odds:.3f}, back to p {back:.3f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

(Values you may use: `ln(4) = 1.386`.)

## Example

For `p = 0.75` the line would be `p=0.75: odds 3.000, log-odds 1.099, back to p 0.750`.

## After you answer

- What do you notice about the log-odds of `p = 0.2` and `p = 0.8`? Why?
