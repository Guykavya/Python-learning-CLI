# Read an experiment by hand

Chapters 2.4 and 2.5. A finished test is summarised by four numbers: the conversion rate of each group, the **absolute** lift (in percentage points), the **relative** lift (in percent of A), and the
randomisation check. This program computes them from the raw counts of a small test.

```python
visitors = {"A": 5100, "B": 4900}
converted = {"A": 255, "B": 294}

rate_a = converted["A"] / visitors["A"]
rate_b = converted["B"] / visitors["B"]
print(f"A {rate_a:.2%} | B {rate_b:.2%}")
print(f"absolute lift {(rate_b - rate_a) * 100:+.2f} points")
print(f"relative lift {(rate_b - rate_a) / rate_a:+.1%}")

total = visitors["A"] + visitors["B"]
expected = total / 2
chi2 = sum((v - expected) ** 2 / expected for v in visitors.values())
print(f"SRM chi-square {chi2:.2f}")
print("SRM verdict:", "MISMATCH" if chi2 > 10.83 else "ok")
```

(For two groups, a chi-square above **10.83** means p < 0.001.) Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `visitors = {"A": 100, "B": 100}` and `converted = {"A": 5, "B": 6}` the first line would be `A 5.00% | B 6.00%`.

## After you answer

- Is the lift of B "big"? What would you want to see next (hint: an interval)?
- The groups differ by 200 visitors: is that a problem?
