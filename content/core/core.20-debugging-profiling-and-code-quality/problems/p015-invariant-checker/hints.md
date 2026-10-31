## Hint 1

What do you need to **remember** from earlier entries to check the current one? Three things:
the ids seen so far, the previous entry's date, and the running balance. Which data type makes
"was this id already used?" a fast question?

## Hint 2

One loop with `enumerate`, three checks in the fixed order, then update what you remember.

```
problems = []; seen = set(); previous = None; balance = opening
for i, entry in enumerate(entries):
    if id in seen: add "duplicate id"
    seen.add(id)
    if previous is not None and date < previous: add "date ... is before ..."
    previous = date
    balance += amount
    if balance < 0: add "balance ... is negative"
return problems
```
