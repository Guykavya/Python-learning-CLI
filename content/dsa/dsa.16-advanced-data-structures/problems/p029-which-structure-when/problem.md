# Which structure when?

The decision questions of chapter section 18, written as a small function: does the data change, what is the operation, what kind of update, are the questions known in advance? Predict **exactly** what this program prints for the eight scenarios. Do not run it.

```python
def choose(changes, op, update, offline):
    if not changes:
        if op == "sum":
            return "prefix sums"
        if op in ("min", "max", "gcd"):
            return "sparse table"
        if offline:
            return "Mo's algorithm"
        return "segment tree"
    if update == "range":
        if op == "sum":
            return "two Fenwick trees"
        return "lazy segment tree"
    if op in ("sum", "count", "xor"):
        return "Fenwick tree"
    return "segment tree"

scenarios = [
    ("highest price in [l, r), prices fixed", False, "max", None, False),
    ("sales total of [l, r), data fixed", False, "sum", None, False),
    ("distinct items in [l, r), all questions known", False, "distinct", None, True),
    ("stock edits one slot, total of [l, r)", True, "sum", "point", False),
    ("sensor edits one reading, lowest in [l, r)", True, "min", "point", False),
    ("bonus to a range of players, total of [l, r)", True, "sum", "range", False),
    ("discount on a range of items, cheapest in [l, r)", True, "min", "range", False),
    ("player joins or leaves, how many scores below x", True, "count", "point", False),
]
for i, (name, changes, op, update, offline) in enumerate(scenarios, 1):
    print(f"{i}. {name}: {choose(changes, op, update, offline)}")
```

Write your answer in `answer.txt`, one printed line per line.

## How to work

For each scenario, read its four values `(changes, op, update, offline)` and walk through `choose` line by line, as the interpreter would. Stop at the first `return` that is reached.

## After you answer

1. For each line, say in a few words **why** the chosen structure fits (chapter section 18, "The table").
2. Scenario 8 is a count. Why does a Fenwick tree fit, and what must you do with the scores first (they go up to 10**9)?
3. Find a scenario where this little function gives a poor answer. (Hint: "distinct items in `[l, r)`, questions arrive one at a time, data fixed".) What would you use instead?
