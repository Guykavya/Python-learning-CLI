## Approach

The state `k` is "how many pattern letters are matched right now". A mismatch does not restart: it falls back to the longest border of the matched part (`pi[k - 1]`) and tries again with the **same** text letter.

## Expected output

```text
i=0 a: k 0 => 1
i=1 a: k 1 => 2
i=2 a: k 2 -> 1 => 2
i=3 b: k 2 => 3
i=4 a: k 3 => 4
i=5 a: k 4 => 5
i=6 a: k 5 -> 2 -> 1 => 2
i=7 b: k 2 => 3
found: []
```

## Why

| i | letter | k before | fallbacks | compared with | k after |
|---|---|---|---|---|---|
| 0 | a | 0 | | `p[0] = a` | 1 |
| 1 | a | 1 | | `p[1] = a` | 2 |
| 2 | a | 2 | → 1 | `p[2] = b` ✗, `p[1] = a` ✓ | 2 |
| 3 | b | 2 | | `p[2] = b` | 3 |
| 4 | a | 3 | | `p[3] = a` | 4 |
| 5 | a | 4 | | `p[4] = a` | 5 |
| 6 | a | 5 | → 2 → 1 | `p[5] = b` ✗, `p[2] = b` ✗, `p[1] = a` ✓ | 2 |
| 7 | b | 2 | | `p[2] = b` | 3 |

`k` never reaches 6, so nothing is found: `found: []`.

**After you answer.**

1. Before `i = 6`, the text letters at positions 1 to 5, `aabaa`, were matched. Its longest border is `aa` (`pi[4] = 2`); `aa` + `a` does not continue the pattern (`aab` needs `b`), so KMP falls to the border of `aa`, which is `a` (`pi[1] = 1`), and `a` + `a` = `aa` matches the pattern's start.
2. At start 1, the text `aabaaa` matches the first five letters `aabaa` and fails on the sixth.
3. One comparison per line without a fallback (6 lines), 2 for `i = 2` and 3 for `i = 6`: 11 comparisons for 8 letters.

## Another way

Check the result with Python: `"aaabaaab".find("aabaab")` is `-1`. The trace shows **why**: the closest attempt (start 1) fails on its last letter.
