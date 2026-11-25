## Hint 1

What do the three mechanisms have in common, and what differs? If each row has a weight, how do you turn the weights into
probabilities whose average is the target rate? How do you compare "income above the median" for a whole column at once?
Which call of the random generator gives one number in [0, 1) per row?

## Hint 2

```text
n = len(pop)
w = ones(n)                                   # MCAR
w = where(age < 40, 2, 1)                     # MAR
w = where(income > income.median(), 5, 1)     # MNAR
anything else -> raise ValueError
p = clip(rate * w / w.mean(), 0, 1)
hide = rng.random(n) < p
out = pop.copy();  out.loc[hide, "income"] = nan
```
