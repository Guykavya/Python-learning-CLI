# Characterize, then refactor

`starter.py` holds `legacy_report(rows)`: 57 lines, `if` blocks nested up to **eleven** levels
deep, and `skipped = skipped + 1` repeated five times. Nobody dares to touch it. Your job
is to make it readable **without changing a single character of its output**.

The safe way, in order:

1. **Characterize.** Before editing, run the function on a few inputs and write down what
   comes out (the tests do this for you with a golden table of 17 cases, taken from the legacy
   code itself: empty input, one row, ties, bad rows, rounding...). They pass on the starter.
2. **Refactor in small steps**, running the tests after each step: flatten with early
   `continue`/`return`, extract a helper, rename, repeat.
3. **Keep going until the structure rules hold**, and the golden table is still green.

**What the report is** (read the code for the exact rules; this is the summary)

Each row is a dict with `name`, `dept`, `amount`, `status`.

- `status == "void"` rows are ignored completely.
- A row is **skipped** (and counted) if the name or dept is empty/blank/missing, the
  amount is not a non-negative number (`bool` does not count), or the status is not `paid`
  or `pending`.
- Departments are stripped and title-cased, then listed in sorted order. For each: row
  count, paid sum, pending sum, and the **top** row (largest amount; on a tie the
  alphabetically first name).
- Last come a `TOTAL` line, and `SKIPPED: n` if `n > 0`. With no valid rows the report is
  `REPORT` then `no data`.

**Structure rules** (checked with `ast`)

- Every function (helpers included) is at most **15 lines**, counting the `def` line.
- No function nests `if`/`for`/`while`/`try`/`with` more than **3** levels deep.
- The module has at least **4** functions, and `legacy_report(rows)` keeps its name.

**Example**

```python
legacy_report([{"name": "Ana", "dept": "eng", "amount": 100, "status": "paid"}])
# 'REPORT\n== Eng ==\n  rows: 1  paid: 100.00  pending: 0.00\n  top: Ana (100.00)\nTOTAL paid: 100.00  pending: 0.00'
```
