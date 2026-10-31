## Approach

Each invariant needs a small piece of **memory** from the earlier entries:

| Invariant | Remember |
|---|---|
| ids are unique | a `set` of ids seen so far (O(1) membership) |
| dates never go backwards | the previous entry's date |
| balance never negative | the running balance |

Go through the entries once. For each one, run the three checks in the fixed order, then
update the memory. Updating **always**, even after a problem, matters: the balance after a
duplicate entry still includes its amount, because that is what the real system did.

Why collect messages instead of `assert`? An `assert` stops at the first broken invariant. That
is perfect inside a program while debugging (it stops right where the data first went wrong).
When you are inspecting a **file** of data, you want the full list, so you can see whether one
bug or several are behind it.

## Code

```python
def ledger_problems(entries: list[dict], opening: int = 0) -> list[str]:
    problems = []
    seen_ids = set()
    previous_date = None
    balance = opening
    for i, entry in enumerate(entries):
        entry_id, date, amount = entry["id"], entry["date"], entry["amount"]
        if entry_id in seen_ids:
            problems.append(f"entry {i}: duplicate id {entry_id!r}")
        seen_ids.add(entry_id)
        if previous_date is not None and date < previous_date:
            problems.append(f"entry {i}: date {date} is before {previous_date}")
        previous_date = date
        balance += amount
        if balance < 0:
            problems.append(f"entry {i}: balance {balance} is negative")
    return problems
```

## Complexity

O(n) time for n entries (set lookups are O(1) on average), O(n) space for the ids.

## Another way

Write one small checker function per invariant, each a generator that yields
`(index, order, message)`, then merge and sort the results by `(index, order)`. More code for
three rules, but adding a fourth invariant then means adding one function, not editing a loop.

While debugging a program (not a file), the same invariants can live in the code as
`assert balance >= 0, f"balance {balance} after {entry}"`. The assert documents the rule and
stops at the first violation, with the message telling you which entry did it.
