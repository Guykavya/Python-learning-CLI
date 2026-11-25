# Read an interval against a threshold

Chapter section 6.2. Compare a confidence interval with the **minimum effect of interest** (MEI), the smallest effect that would
change a decision. Three honest outcomes: entirely above, entirely below, or straddling. Note what happens when an end is **exactly**
on the MEI.

```python
MEI = 0.5


def verdict(lo, hi, mei=MEI):
    if lo > mei:
        return "worth it: the whole interval is above the minimum effect"
    if hi < mei:
        return "not worth it: the whole interval is below the minimum effect"
    return "inconclusive: the interval contains the minimum effect"


for lo, hi in [(0.60, 1.20), (0.50, 0.90), (0.10, 0.50), (-0.40, 0.30), (-1.00, 2.00)]:
    print(f"[{lo:5.2f}, {hi:5.2f}] {verdict(lo, hi).split(':')[0]}")
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Mind the width of `:5.2f` (it pads to 5
characters, including the minus sign).

Do not run the code before you have written your answer.

## Example

For `[0.70, 0.90]` the line would be `[ 0.70,  0.90] worth it`.

## After you answer

- Why is `[0.50, 0.90]` not "worth it" although every plausible value is at least 0.5?
- Which of the five intervals would a plain "p < 0.05" test have called significant?
