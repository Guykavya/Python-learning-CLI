## Hint 1

What is the first number you need before measuring any distance? Then what do you sum, and by what do you divide for the population and for the sample?

## Hint 2

```text
validate ddof in (0, 1) and len(values) - ddof >= 1
m = sum(values) / n
ss = sum((x - m) ** 2 for x in values)
return ss / (n - ddof)
```
