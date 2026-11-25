## Hint 1

Which centre and which spread do you need before you can compute a standardised deviation? Which of the two standard deviations does the formula name?

## Hint 2

```text
n = len(values); validate n >= 3
m = mean; sd = population sd (sqrt of sum((x-m)**2) / n); if sd == 0: ValueError
return sum(((x - m) / sd) ** 3 for x in values) / n
```
