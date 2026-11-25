## Hint 1

How many decimals does an uncertainty of 63 justify, one of 5.9, one of 0.4? What does `log10` tell you about the size of a number? What do you do when there is no usable uncertainty?

## Hint 2

```text
if ref == 0 or not isfinite(ref): return f"{value:,.0f}"
decimals = max(0, 1 - floor(log10(abs(ref))))
return f"{round(value, decimals):,.{decimals}f}"
```
