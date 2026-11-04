## Approach

A **variable-size sliding window**. The window `s[l..r]` always holds distinct characters. Moving `r` right adds
one character; if that character is already inside, `l` moves right, dropping characters, until the old copy
is gone. Both pointers only move forward, so each character enters and leaves the window at most once.

After each step the window is the longest repeat-free substring that **ends at `r`**. The best of those over all
`r` is the answer. Updating only on a strictly longer window keeps the earliest start on ties.

## Code

```python
s = input()

seen = set()          # the characters inside the window s[l..r]
l = 0
best_len, best_start = 0, 0
for r in range(len(s)):
    while s[r] in seen:           # shrink until s[r] is no longer inside
        seen.remove(s[l])
        l += 1
    seen.add(s[r])
    if r - l + 1 > best_len:      # strictly longer: ties keep the earlier start
        best_len, best_start = r - l + 1, l

print(best_len)
print(s[best_start:best_start + best_len])
```

On `pwwkew`:

| r | s[r] | dropped | window | best |
|---|---|---|---|---|
| 0 | p | | p | 1 (p) |
| 1 | w | | pw | 2 (pw) |
| 2 | w | p, w | w | 2 |
| 3 | k | | wk | 2 |
| 4 | e | | wke | 3 (wke) |
| 5 | w | w | kew | 3, a tie, so wke stays |

## Complexity

O(n) time: `r` moves `n` times and `l` moves at most `n` times in total, even though there is a `while` inside the
`for`. O(k) extra memory, where `k` is the number of different characters (at most 94 here).

## Another way

Store the **last index** of every character in a dictionary. When `s[r]` was last seen at position `p >= l`, jump
straight to `l = p + 1` instead of dropping one character at a time. Same O(n), fewer steps. Be careful to use
`max(l, p + 1)`: an old position from before the window must not move `l` backwards (try `abba`).
