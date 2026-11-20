## Approach

Keep `k`, the length of the current border, and try to extend it by the letter `s[k]`. On a mismatch, fall back to the longest border **of the border**, `pi[k - 1]`, never to 0 directly.

## Expected output

```text
1 b [0] 0
2 a [0] 1
3 c [1, 0] 0
4 a [0] 1
5 b [1] 2
6 a [2] 3
7 b [3, 1] 2
[0, 0, 1, 0, 1, 2, 3, 2]
```

## Why

| i | s[i] | k before | compared with | result |
|---|---|---|---|---|
| 1 | b | 0 | `s[0] = a` | no: 0 |
| 2 | a | 0 | `s[0] = a` | yes: 1 |
| 3 | c | 1 | `s[1] = b`, then `s[0] = a` | no, fall back to 0, no: 0 |
| 4 | a | 0 | `s[0] = a` | yes: 1 |
| 5 | b | 1 | `s[1] = b` | yes: 2 |
| 6 | a | 2 | `s[2] = a` | yes: 3 |
| 7 | b | 3 | `s[3] = c`, then `s[1] = b` | no, fall back to `pi[2] = 1`, yes: 2 |

**After you answer.**

1. The border `aba` (length 3) needs `c` next, but the text has `b`. Its longest border is `a` (`pi[2] = 1`); `a` followed by `b` gives `ab`, the final border of `abacabab`.
2. The longest border is `ab` (2), so the smallest period is `8 - 2 = 6`: `abacab|ab` repeats the first two letters of `abacab`.
3. Count the comparisons: one per `i` without a fallback (5 rows), and two for rows 3 and 7: 9 comparisons in all, well below `2n = 16`.

## Another way

Check with the definition: for `abacabab`, try every `k` from 7 down: is `s[:k] == s[-k:]`? The first equal pair is at `k = 2` (`ab`). That checks only `pi[7]`, but it is a good habit for the last value.
