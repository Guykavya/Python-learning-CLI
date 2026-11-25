# Cohort retention by hand

Chapter section 4.2. Six customers, four months numbered 0 to 3 (the data end in month 3). `signup` gives each customer's first month; `active` gives the months in which they ordered.

```python
signup = {"a": 0, "b": 0, "c": 1, "d": 1, "e": 2, "f": 3}
active = {"a": {0, 1, 3}, "b": {0}, "c": {1, 2}, "d": {1, 3}, "e": {2, 3}, "f": {3}}
LAST = 3
for cohort in range(4):
    members = [c for c, s in signup.items() if s == cohort]
    row = []
    for k in range(4):
        if cohort + k > LAST:
            row.append("-")
        else:
            n = sum(1 for c in members if cohort + k in active[c])
            row.append(f"{n / len(members):.2f}")
    print(cohort, len(members), " ".join(row))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. A `-` marks a cell that has not happened yet. Do not run the code before you have written your answer.

## Example

For a cohort of one customer who ordered in the first month and the second month, with data to the second month, the line would be `0 1 1.00 1.00 - -`.

## After you answer

- Why is the last cell of the cohort-1 row `-` and not `0.00`?
- Which cohort's month-1 retention is the highest, and does a tiny cohort deserve the same trust?
