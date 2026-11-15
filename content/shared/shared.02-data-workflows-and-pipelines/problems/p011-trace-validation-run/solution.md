## Approach

Trace each record through `check` and `transform`, remember that the `BAD` lines are printed
only by the `finally` block (after all `OK` lines of that run), and check the threshold at the end.

**batch1** (`max_bad=0.5`)

| id | check | transform | result |
|---|---|---|---|
| 1 | ok | `"Shipped"` -> `shipped`; `Z` -> `+00:00` | `OK 1 shipped 10.50 2024-06-01T10:00:00+00:00` |
| `"2"` | `id: not int` (status and amount are fine) | not called | quarantined |
| 3 | `status: null; amount: not str` (7 is an int) | not called | quarantined |
| `True` | passes: `isinstance(True, int)` is `True` | `" PENDING "` -> `pending`, `Decimal("0")` prints `0`, offset kept | `OK True pending 0 2024-06-02T09:00:00+05:30` |
| 5 | ok | `rec["created_at"]` -> `KeyError` (caught) | quarantined, reason `KeyError` |

`finally` prints the three `BAD` lines; `3 / 5 = 0.6 > 0.5`, so `batch1 2 3 ABORT`.

**batch2** (`max_bad=0.3`)

| id | transform | result |
|---|---|---|
| 6 | `Decimal(" 4.25 ")` is `4.25`; `"2024-06-03"` is midnight, no offset | `OK 6 cancelled 4.25 2024-06-03T00:00:00` |
| 7 | 30 February -> `ValueError` (caught) | quarantined |
| 8 | `Decimal("1e3")` is valid and prints as `1E+3` | `OK 8 shipped 1E+3 2024-06-03T08:00:00+00:00` |

`1 / 3 = 0.333... > 0.3`, so `batch2 2 1 ABORT`.

**batch3**: id 9 is OK. Id 11 has no `created_at`: `KeyError`, quarantined. Id 10:
`Decimal("12,00")` raises `decimal.InvalidOperation`, which is an `ArithmeticError`, not a
`ValueError`, so the inner `except` does not catch it. The outer `except Exception` prints
`CRASH InvalidOperation at id 10` and returns; on the way out, `finally` prints the one `BAD`
line. The summary line is never reached, and id 12 is never processed.

## Full output

```
OK 1 shipped 10.50 2024-06-01T10:00:00+00:00
OK True pending 0 2024-06-02T09:00:00+05:30
BAD {"id": "2", "reason": "id: not int"}
BAD {"id": 3, "reason": "status: null; amount: not str"}
BAD {"id": 5, "reason": "KeyError"}
batch1 2 3 ABORT
OK 6 cancelled 4.25 2024-06-03T00:00:00
OK 8 shipped 1E+3 2024-06-03T08:00:00+00:00
BAD {"id": 7, "reason": "ValueError"}
batch2 2 1 ABORT
OK 9 shipped 2.50 2024-06-04T08:00:00+00:00
CRASH InvalidOperation at id 10
BAD {"id": 11, "reason": "KeyError"}
```

## Complexity

One pass over each batch. What matters here is not speed but which records slip through.

## Another way

Each trap points to a fix in real code: reject `bool` explicitly in the type check (the order
with id `True` was "loaded"); catch `Exception` per record so one bad amount cannot crash the
run (batch3 lost id 12 and the good id 9 was never loaded); require an offset on timestamps
(id 6 has none); and add a range or format check on amounts, because `"1e3"` parses fine but
is almost certainly not what the source meant.
