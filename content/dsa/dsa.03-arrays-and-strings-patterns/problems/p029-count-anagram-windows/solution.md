## Approach

A **fixed-size sliding window** with letter counts. Being an anagram depends only on the counts of the 26 letters,
so keep those counts for the window and update them in O(1) when the window slides: one letter comes in on the
right, one goes out on the left. The window is complete from `r = m - 1` on; from then, compare the counts.

## Code

```python
text = input()
pattern = input()
n, m = len(text), len(pattern)

need = [0] * 26
for ch in pattern:
    need[ord(ch) - ord("a")] += 1

have = [0] * 26
count = 0
for r in range(n):
    have[ord(text[r]) - ord("a")] += 1          # character entering the window
    if r >= m:
        have[ord(text[r - m]) - ord("a")] -= 1  # character leaving the window
    if r >= m - 1 and have == need:             # the window text[r-m+1 .. r] is full
        count += 1

print(count)
```

When `m > n`, the condition `r >= m - 1` is never true, so the answer is 0 with no special case.

## Complexity

O(26 * n + m) time: one O(1) update and one 26-element comparison per position. O(1) extra memory (two lists of
26). Building `sorted(window)` for every window would cost O(n * m log m).

## Another way

Keep one extra number, `matches`: how many of the 26 letters currently have `have[c] == need[c]`. Each update
changes one letter's count, so adjust `matches` by looking at that letter only. The window is an anagram when
`matches == 26`. That makes each step O(1) instead of O(26), and it is the trick behind the minimum-window
substring problem later in this module.
