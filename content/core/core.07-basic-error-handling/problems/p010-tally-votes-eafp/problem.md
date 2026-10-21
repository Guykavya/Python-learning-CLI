# Tally votes, EAFP style

Write `tally(votes)` that takes a list of vote strings and returns a dict from candidate to
number of votes.

- Clean each vote with `.strip().lower()` before counting it, so `" Asha"` and `"ASHA"` count
  for `"asha"`.
- Skip votes that are empty after cleaning.
- Count in **EAFP** style (chapter section 14): try `counts[name] += 1`, and handle the
  `KeyError` for a first vote. Do not use `dict.get`, `in`, or `setdefault` for this
  problem; they are good tools, but this problem practises the `try` form.

**Example**

```python
tally(["Asha", " ravi", "ASHA", "", "Meena ", "asha", "   "])
# {'asha': 3, 'ravi': 1, 'meena': 1}
```
