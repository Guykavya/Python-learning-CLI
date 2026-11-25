# Log-loss by hand

Chapter section 12. **Log-loss** (cross-entropy) judges the probabilities themselves. For a positive case (y = 1) the loss is `-ln(p)`: small if the model said high, huge if it said nearly 0. A probability of exactly 0 would give infinite loss, so it is **clipped** into `[eps, 1 - eps]` first.

```python
import math


def contribution(y, p, eps=1e-15):
    p = min(max(p, eps), 1 - eps)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


probabilities = [0.9, 0.5, 0.1, 0.0]
losses = []
for p in probabilities:
    loss = contribution(1, p)
    losses.append(loss)
    print(f"y=1, p={p}: loss {loss:.3f}")
print(f"mean log-loss: {sum(losses) / len(losses):.3f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

(Values you may use: `ln(0.9) = -0.10536`, `ln(0.5) = -0.69315`, `ln(0.1) = -2.30259`, `ln(10) = 2.30259`.)

## Example

For `y = 1` and `p = 0.8` the line would be `y=1, p=0.8: loss 0.223`.

## After you answer

- Why is the last prediction (`p = 0.0` for a case that **is** positive) so expensive, and what does the clip `eps = 1e-15` do? What would happen without it?
