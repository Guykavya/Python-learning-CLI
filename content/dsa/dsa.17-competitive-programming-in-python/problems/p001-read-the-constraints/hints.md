## Hint 1

What is the budget in operations for `s` seconds? Which of the seven costs is the largest one that still fits under it?

## Hint 2

Compute the cost of all seven classes, keep the ones that fit under the budget, and print the one that comes **last** in the table. (For tiny `n` the table order is not strict: `n = 3` gives `2**n = 8` but `n**3 = 27`. A loop that overwrites `best` for every class that fits handles this without thinking.)

## Hint 3

```text
budget = 10**7 * s
for each name, cost in the table:
    if cost <= budget: best = name   # later rows overwrite earlier ones
print best
```

Careful with `2 ** n` when `n = 10**9`: it would take forever. If `n > 60`, `2^n` can never fit in a budget of at most `10**8`, so skip it.
