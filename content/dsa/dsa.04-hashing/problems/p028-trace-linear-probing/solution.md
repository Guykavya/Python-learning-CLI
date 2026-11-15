## Walkthrough

| key | home slot | slots tried | placed in |
|---|---|---|---|
| 10 | 3 | 3 | 3 |
| 17 | 3 | 3, 4 | 4 |
| 3 | 3 | 3, 4, 5 | 5 |
| 24 | 3 | 3, 4, 5, 6 | 6 |
| 8 | 1 | 1 | 1 |
| 15 | 1 | 1, 2 | 2 |

Final table: `[None, 8, 15, 10, 17, 3, 24]`. Slot 0 is the only empty slot.

## Output

```
put 10 probes [3]
put 17 probes [3, 4]
put 3 probes [3, 4, 5]
put 24 probes [3, 4, 5, 6]
put 8 probes [1]
put 15 probes [1, 2]
[None, 8, 15, 10, 17, 3, 24]
find 3 found [3, 4, 5]
find 1 missing [1, 2, 3, 4, 5, 6, 0]
find 31 missing [3, 4, 5, 6, 0]
```

## Key ideas

- A **cluster** of full slots (3 to 6) makes every later key with a home inside it probe longer: this is why open addressing
  must be kept well below full (a low load factor).
- A search can stop at the first empty slot: if the key had been inserted, the insert would have used that slot or an earlier one.
- Deleting by emptying a slot breaks that rule. Real implementations mark the slot as a **tombstone**.
