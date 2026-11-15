# Trace sorting by two keys in two passes

Predict **exactly** what this program prints. Do not run it.

```python
people = [("ann", 30), ("bob", 25), ("cy", 30), ("dee", 25), ("eli", 35)]
step1 = sorted(people, key=lambda p: p[0], reverse=True)
print(step1)
step2 = sorted(step1, key=lambda p: p[1])
print(step2)
wrong = sorted(sorted(people, key=lambda p: p[1]), key=lambda p: p[0], reverse=True)
print(wrong)
print(step2 == sorted(people, key=lambda p: (p[1], [-ord(c) for c in p[0]])))
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

`step1` sorts by **name descending** (the less important key). `step2` then sorts by **age ascending** (the more important key). The second sort is stable, so people of equal age
stay in the name order of `step1`. `wrong` runs the passes in the opposite order. The last line compares `step2` with a one-shot sort whose key negates every letter code of the name, so equal ages are ordered by name descending as well.

## After you answer

1. Which pass decides the *primary* ordering? Which pass only decides ties?
2. Why does `wrong` end up ordered by name (descending) first and age only for equal names?
3. What does the final `True` or `False` tell you about the two-pass method versus a tuple key?
