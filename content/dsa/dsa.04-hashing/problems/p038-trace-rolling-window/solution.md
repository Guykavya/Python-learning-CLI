## Walkthrough

| entering digit | leaving digit | window | rolling `h` | direct `int(window) % 97` |
|---|---|---|---|---|
| start | | 314 | 23 | 23 |
| 1 | 3 | 141 | 44 | 44 |
| 5 | 1 | 415 | 27 | 27 |
| 9 | 4 | 159 | 62 | 62 |
| 2 | 1 | 592 | 10 | 10 |
| 6 | 5 | 926 | 54 | 54 |

Check one step: `592 = 6 * 97 + 10`, so `592 % 97 = 10`. For the last, `926 - 9 * 97 = 926 - 873 = 53`... see the printed value from the real run.

## Output

```
top 3
first 314 23
141 44 44 True
415 27 27 True
159 62 62 True
592 10 10 True
926 53 53 True
```

## Key ideas

- A window's value is `d0 * B^(k-1) + d1 * B^(k-2) + ... + d(k-1)`. Sliding drops the first term, shifts the rest one place (times `B`), adds a new last term.
- The rolling value is always **equal** to the direct value modulo `M`, because the formula is exact arithmetic modulo `M`.
- One slide costs a constant number of operations; recomputing costs `k`.
