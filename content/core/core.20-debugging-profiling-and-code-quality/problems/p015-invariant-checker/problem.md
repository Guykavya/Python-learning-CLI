# Invariant checker

An **invariant** is a fact that must be true at every step: "the balance is never negative",
"ids are unique", "dates never go backwards". When a bug corrupts data, it usually breaks an
invariant long before anything crashes. Checking the invariants is therefore one of the fastest
ways to find **where** the corruption started: the first broken invariant points at the guilty
entry.

`assert` checks one invariant and stops at the first failure. For debugging a whole data file
it is more useful to collect **every** problem in one pass.

Write `ledger_problems(entries: list[dict], opening: int = 0) -> list[str]` in `solution.py`.
Each entry is a dict `{"id": str, "date": "YYYY-MM-DD", "amount": int}` (amounts in paise:
positive is money in, negative is money out). Start with `balance = opening`. Go through the
entries in order; for the entry at index `i` (from 0):

1. If its `id` was already used by an earlier entry:
   `f"entry {i}: duplicate id {id!r}"`
2. If its date is **before the previous entry's date**:
   `f"entry {i}: date {date} is before {previous_date}"`
3. Add its amount to the balance (always, even if the entry had problems). If the balance is
   now negative: `f"entry {i}: balance {balance} is negative"`

Return all messages in order (for one entry, in the order 1, 2, 3). Return `[]` when every
invariant holds. Do not change the entries.

ISO dates (`YYYY-MM-DD`) compare correctly as plain strings, so `"2026-01-09" < "2026-01-10"`
works without converting them.

**Example**

```python
entries = [
    {"id": "a1", "date": "2026-03-01", "amount": 5000},
    {"id": "a2", "date": "2026-03-04", "amount": -7000},
    {"id": "a1", "date": "2026-03-02", "amount": 1000},
    {"id": "a3", "date": "2026-03-05", "amount": 2500},
]
ledger_problems(entries)
# ['entry 1: balance -2000 is negative',
#  "entry 2: duplicate id 'a1'",
#  'entry 2: date 2026-03-02 is before 2026-03-04',
#  'entry 2: balance -1000 is negative']
```

Entry 3 is fine: the balance is back to 1500, and `2026-03-05` is after `2026-03-02`.
