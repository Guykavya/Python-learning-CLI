# Calibration moves the best threshold

Chapter sections 10 and 11. A retention call costs **20**; a churner we do not call costs **100**. So call a customer when the expected loss of not calling, `p * 100`, is larger than the cost of the call, 20, i.e. when `p >= 0.2`. That rule is only right if `p` is a **calibrated** probability.

A model sorts customers into four score bins. For each bin we know the model's probability and, from a held-out set, the **observed** churn rate:

```python
CALL, MISS = 20, 100
THRESHOLD = CALL / MISS

bins = [("A", 0.05, 0.10), ("B", 0.15, 0.30), ("C", 0.30, 0.55), ("D", 0.60, 0.85)]   # (bin, model p, observed rate)

raw = [name for name, p, obs in bins if p >= THRESHOLD]
calibrated = [name for name, p, obs in bins if obs >= THRESHOLD]
print(f"threshold: {THRESHOLD}")
print(f"call with model probabilities: {', '.join(raw)}")
print(f"call with calibrated probabilities: {', '.join(calibrated)}")
name, p, obs = bins[1]
print(f"bin {name} expected cost per customer: skip {obs * MISS:.1f}, call {CALL:.1f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

If bin A had a model probability of 0.25, it would be in both lists.

## After you answer

- Which customers does the uncalibrated model fail to call, and what does that cost per 100 such customers?
