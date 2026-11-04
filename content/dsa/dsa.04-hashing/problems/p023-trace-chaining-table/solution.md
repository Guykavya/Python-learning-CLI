## Walkthrough

| key | key % 4 | action | chain afterwards |
|---|---|---|---|
| 5 | 1 | new | [5] |
| 9 | 1 | new, collides with 5 | [5, 9] |
| 12 | 0 | new | [12] |
| 13 | 1 | new, collides | [5, 9, 13] |
| 5 | 1 | already there | unchanged |
| 7 | 3 | new | [7] |
| 16 | 0 | new | [12, 16] |
| 1 | 1 | new | [5, 9, 13, 1] |
| 20 | 0 | new | [12, 16, 20] |

Final buckets: `[[12, 16, 20], [5, 9, 13, 1], [], [7]]`.

## Output

```
put 5 bucket 1 chain length 1
put 9 bucket 1 chain length 2
put 12 bucket 0 chain length 1
put 13 bucket 1 chain length 3
put 5 bucket 1 already there
put 7 bucket 3 chain length 1
put 16 bucket 0 chain length 2
put 1 bucket 1 chain length 4
put 20 bucket 0 chain length 3
[[12, 16, 20], [5, 9, 13, 1], [], [7]]
find 13 found after 3 steps
find 100 missing after 3 steps
find 7 found after 1 steps
```

## Key ideas

- Keys 5, 9, 13, 1 all have remainder 1 modulo 4: they **collide** and share a chain.
- A lookup costs the length of one chain, not the size of the table. Long chains mean slow lookups.
- Unlucky keys (all multiples of 4) would put everything in one bucket and the table would behave like a list.
