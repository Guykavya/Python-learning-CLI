# Explain: why groupby needs sorted input

Nisha wants the total quantity for each drink. She runs:

```python
from itertools import groupby

sales = [("tea", 3), ("coffee", 5), ("tea", 2), ("juice", 1), ("coffee", 4)]

for name, group in groupby(sales, key=lambda s: s[0]):
    print(name, sum(qty for _, qty in group))

print("---")
groups = groupby(sorted(sales), key=lambda s: s[0])
saved = {name: group for name, group in groups}
print({name: list(g) for name, g in saved.items()})
```

Output:

```text
tea 3
coffee 5
tea 2
juice 1
coffee 4
---
{'coffee': [], 'juice': [], 'tea': []}
```

She expected `tea 5`, `coffee 9`, `juice 1`, and three full lists at the end.

In `answer.md` (about 150 to 300 words), explain:

1. What exactly does `groupby` group together? Why does `tea` appear twice in the first part?
2. Why does sorting the input first fix the first part? What is the cost of sorting, and when is it
   **not** needed (for example, log lines that are already in time order)?
3. Why are all the lists empty in the second part, even though the input was sorted? What is a
   `group` object, and what happens to it when `groupby` moves on to the next key?
4. Show how to fix the second part.
5. When would a plain dict (`totals[name] = totals.get(name, 0) + qty`) be a better choice than
   `sorted` + `groupby`?
