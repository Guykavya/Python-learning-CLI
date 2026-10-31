# Trace: alias, shallow copy, deep copy

Three ways to "copy" a nested structure give three different amounts of sharing:

- `alias = team` copies nothing. Both names point to the **same** object.
- `copy.copy(team)` (a **shallow** copy) makes a new outer container, but the values inside it are
  the same objects as in the original.
- `copy.deepcopy(team)` makes a new outer container **and** new copies of everything inside,
  all the way down.

Slicing (`rows[:]`), `list(rows)` and `dict(d)` are shallow copies too. Immutable objects (numbers,
strings, tuples of immutable things) never need copying, and `copy` knows that.

Predict **every line** this program prints:

```python
import copy

team = {"name": "A", "members": ["ann", "bo"], "meta": {"level": 1}}
alias = team
shallow = copy.copy(team)
deep = copy.deepcopy(team)

shallow["name"] = "B"
shallow["members"].append("cy")
deep["meta"]["level"] = 9
alias["meta"]["level"] = 2

print("A", team["name"], shallow["name"], deep["name"])
print("B", team["members"])
print("C", deep["members"])
print("D", team["meta"]["level"], shallow["meta"]["level"], deep["meta"]["level"])
print("E", shallow["members"] is team["members"], deep["members"] is team["members"])
print("F", alias is team, shallow is team, shallow == team)

rows = [[1, 2], [3, 4]]
r2 = rows[:]
r2[0] = [9, 9]
r2[1][0] = 8
print("G", rows)
print("H", r2)

grid = [[0] * 2] * 2
grid[0][0] = 5
print("I", grid)

t = (1, [2])
print("J", copy.copy(t) is t)
t2 = copy.deepcopy(t)
print("K", t2 is t, t2[1] is t[1], t2 == t)
u = (1, "x", (2, 3))
print("L", copy.deepcopy(u) is u)
```

Write your answer in `answer.txt`, one printed line per line, exactly as Python prints it.

**Example** (the first line, given away):

```text
A A B A
```
