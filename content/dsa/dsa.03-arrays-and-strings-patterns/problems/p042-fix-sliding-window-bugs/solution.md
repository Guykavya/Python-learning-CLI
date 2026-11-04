## The three bugs

| # | bug | symptom | fix |
|---|---|---|---|
| 1 | `best = max(best, right - left)` | longest is one too small (`aaaa`, `k = 1` gives 3) | the window `s[left..right]` has `right - left + 1` characters |
| 2 | the count drops to 0 but the key stays | `len(count)` never goes down; with `while` the window shrinks past `right` and crashes (`KeyError`), with `if` it gives wrong counts | `del count[out]` when it reaches 0 |
| 3 | `if len(count) > k` shrinks only one step | line 1 still right, line 2 too big (`eceba`, `k = 2` gives 12 instead of 10) | `while len(count) > k` |

**Why bug 3 hides from line 1.** With `if`, the window grows by one and shrinks by at most one each step, so its
size never decreases. It only grows when the new window is good, so its size is always the best size seen so far,
and line 1 comes out right. But at many steps the window is **not** good, and adding its length to `total` counts
substrings that have too many distinct characters. Any code that uses the window at **every** step (counting,
printing, summing) needs the window to be valid at every step, so it needs `while`.

## Code

```python
s = input().strip()
k = int(input())

count = {}
left = 0
best = 0
total = 0

for right in range(len(s)):
    ch = s[right]
    count[ch] = count.get(ch, 0) + 1
    while len(count) > k:
        out = s[left]
        count[out] -= 1
        if count[out] == 0:
            del count[out]
        left += 1
    best = max(best, right - left + 1)
    total += right - left + 1

print(best)
print(total)
```

`total += right - left + 1` works because every good substring ending at `right` starts somewhere in
`left..right`: if `s[left..right]` has at most `k` distinct characters, so does every shorter piece of it.

## Complexity

O(n) time: `right` moves `n` times and `left` moves at most `n` times in total, over the whole run. The dictionary
holds at most `k + 1` keys, so O(k) extra memory.

## Another way

Instead of counts, keep `last[ch]`, the last index where each letter appeared. The good window ending at `right`
starts just after the `(k + 1)`-th most recent letter. That costs a sort of at most 27 values per step, still
O(26 n). The count dictionary is the general tool; it also works when you need "at most k of each" rules.

This "count of substrings with at most k distinct" is exactly the helper you need for the next problem:
**exactly** `k` distinct = at most `k` minus at most `k - 1`.
