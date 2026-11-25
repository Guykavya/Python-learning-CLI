## Hint 1

Which function turns "95% two-sided" and "80% power" into the two z-values? Which of the two uses `1 - alpha / 2`? Why must the last step round up and not to the nearest?

## Hint 2

```text
z_a = norm.ppf(1 - alpha / 2); z_b = norm.ppf(power)
p1 = p0 + mde; p_bar = (p0 + p1) / 2
return int(ceil(2 * (z_a + z_b) ** 2 * p_bar * (1 - p_bar) / mde ** 2))
```
