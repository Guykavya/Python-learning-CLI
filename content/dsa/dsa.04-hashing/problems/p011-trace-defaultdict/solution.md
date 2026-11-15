## Walkthrough

| word | key (length) | `len(by_len)` after |
|---|---|---|
| tea | 3 | 1 |
| ate | 3 | 1 |
| to | 2 | 2 |
| at | 2 | 2 |
| tan | 3 | 2 |

For `mississippi` the counts are `m 1`, `i 4`, `s 4`, `p 2`.

## Output

```
tea 1
ate 1
to 2
at 2
tan 2
{3: ['tea', 'ate', 'tan'], 2: ['to', 'at']}
{'m': 1, 'i': 4, 's': 4, 'p': 2}
0 5
False 5
```

## Key ideas

- `defaultdict(list)` appends to a fresh list the first time a key appears: no `if key not in d` needed.
- Reading a missing key from a `defaultdict` **creates** it. `total["z"]` makes `len(total)` jump from 4 to 5.
- `"q" in total` never creates a key; use `in` (or `.get`) to ask without changing the dictionary.
