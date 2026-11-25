## Hint 1

Which two sums of squares do you need? What is the model's fitted value if it only knows the mean of y?

## Hint 2

```text
rss = sum((y - fitted)^2)
tss = sum((y - mean(y))^2)
r2  = 1 - rss / tss
adj = 1 - (1 - r2) * (n - 1) / (n - p - 1)
```
