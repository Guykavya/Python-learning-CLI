## Approach

Variable sliding window, "shortest" form. A window is **good** when it covers `t` with multiplicity. Two facts make
the two pointers enough:

- If `s[left..right]` is good, every longer window `s[left..right']` is good too, so for a fixed `left` there is a
  first `right` where it becomes good.
- If you move `left` forward, that first good `right` can only move forward as well.

So `right` grows the window until it is good, and `left` shrinks it while it stays good, recording each good window.
Instead of comparing whole dictionaries, keep `missing`, the number of characters of `t` still lacking. It changes
only when a count crosses its `need`: extra copies do not count.

## Code

```python
s = input().strip()
t = input().strip()

need = {}
for ch in t:
    need[ch] = need.get(ch, 0) + 1

have = {}
missing = len(t)
left = 0
best_len, best_start = len(s) + 1, -1

for right in range(len(s)):
    ch = s[right]
    have[ch] = have.get(ch, 0) + 1
    if have[ch] <= need.get(ch, 0):
        missing -= 1
    while missing == 0:
        if right - left + 1 < best_len:
            best_len, best_start = right - left + 1, left
        out = s[left]
        have[out] -= 1
        if have[out] < need.get(out, 0):
            missing += 1
        left += 1

if best_start == -1:
    print(-1)
else:
    print(s[best_start:best_start + best_len])
```

**Why `<` gives the earliest.** The windows are recorded in order of their right end, and for equal lengths a later
right end means a later start. The first one recorded is the earliest, and `<` never replaces it with an equal one.

## Complexity

O(len(s) + len(t)) time: `right` and `left` each move at most `len(s)` times, and each step is O(1) dictionary work.
O(52) extra memory for the counts. Slicing the answer only once, at the end, avoids copying strings in the loop.

## Another way

Binary search the answer length `L` (from `len(t)` to `len(s)`): a fixed window of size `L` slides across `s`, and you
check whether any position covers `t`. "Some window of length `L` is good" is true for all `L` above the answer and
false below it, so binary search works. That is O(len(s) log len(s)): slower, but a useful check, and the same
"monotone yes/no" idea returns in the binary search module.
