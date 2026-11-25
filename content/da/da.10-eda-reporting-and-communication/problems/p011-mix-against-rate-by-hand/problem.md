# Mix against rate by hand

Chapter section 4.5. An overall rate is the share-weighted sum of the segment rates. When it changes, part of the change comes from the **mix** (the shares moved) and part from the
**rates** (the segments themselves changed). With averaged weights the two parts add up to the total exactly:

```text
mix  = sum over segments of (share after - share before) x (rate before + rate after) / 2
rate = sum over segments of (rate after - rate before)   x (share before + share after) / 2
```

```python
share_b = {"new": 0.20, "old": 0.80}
share_a = {"new": 0.10, "old": 0.90}
rate_b = {"new": 0.10, "old": 0.03}
rate_a = {"new": 0.15, "old": 0.05}
mix = sum((share_a[k] - share_b[k]) * (rate_a[k] + rate_b[k]) / 2 for k in share_b) * 100
rate = sum((rate_a[k] - rate_b[k]) * (share_a[k] + share_b[k]) / 2 for k in share_b) * 100
total_b = sum(share_b[k] * rate_b[k] for k in share_b) * 100
total_a = sum(share_a[k] * rate_a[k] for k in share_b) * 100
print(f"before {total_b:.2f}  after {total_a:.2f}")
print(f"mix {mix:.2f}  rate {rate:.2f}  total {total_a - total_b:.2f}")
print(abs(mix + rate - (total_a - total_b)) < 1e-9)
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

If both shares stayed the same (0.2 and 0.8 after as well), the mix effect would be `0.00`.

## After you answer

- The share of new customers (who churn most) fell. Which way does that push the overall rate, and which number shows it?
- If you only looked at the overall rates (before and after), what would you have missed?
