# The last decimal

Chapter section 11.6. Two differences between Python and Excel decide the last decimal of a report: **how** a half is rounded, and **when** you round (each line, or the total).

```python
from decimal import Decimal, ROUND_HALF_UP


def xl_round(x, n=0):
    d = Decimal(format(float(x), ".15g"))
    return float(d.quantize(Decimal(1).scaleb(-int(n)), rounding=ROUND_HALF_UP))


print(round(0.125, 2), round(2.5), round(1.005, 2), round(2.675, 2))
print(xl_round(0.125, 2), xl_round(2.5), xl_round(1.005, 2), xl_round(2.675, 2))
lines = [10.004, 10.004, 10.004, 10.004]
print(f"{sum(round(v, 2) for v in lines):.2f}")
print(f"{round(sum(lines), 2):.2f}")
```

Python's `round` rounds half to **even** and works on the **binary** value (the float `1.005` is really `1.00499999999999989...`, and `2.675` is `2.67499999999999982...`). `xl_round` reads the number at 15 significant digits and rounds half **away from zero**, like Excel.

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. `0.125` is exactly representable in binary. Do not run the code before you have written your answer.

## Example

For a pair `(0.5, 1.5)` with `round(0.5), round(1.5)` Python prints `0 2` and an Excel-like round gives `1.0 2.0`.

## After you answer

- Which of the four values differ between Python and Excel, and why?
- A report shows 40.02 for the sum of four lines of 10.004, each displayed as 10.00. Who is right, and what should the report say?
