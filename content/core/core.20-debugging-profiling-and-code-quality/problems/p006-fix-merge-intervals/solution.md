## Approach

Reproduce each report with the smallest input, stop inside the loop, look at the names, and
connect each symptom to a line:

| Report | Smallest input | Cause (line) |
|---|---|---|
| touching blocks stay apart | `[[1, 3], [3, 5]]` | `start < last[1]`: should be `<=` |
| full day shrinks to 9-11 | `[[9, 17], [10, 11]]` | `last[1] = end`: should be `max(last[1], end)` |
| my list is re-ordered | `[[8, 10], [1, 3]]` | `intervals.sort()` sorts the caller's list in place |
| my booking's end changed | `[[1, 3], [2, 6]]` | `merged = [intervals[0]]` stores the caller's pair; `last[1] = ...` writes into it |
| crash on `[]` | `[]` | `intervals[0]` on an empty list |
| crash on tuples | `[(1, 2), (2, 4)]` | `last` is the caller's tuple, and tuples cannot be assigned to |

At a `(Pdb)` prompt on the second example, `p last is intervals[0]` prints `True`: that one
line explains two reports. Aliasing bugs are hard to see by reading and easy to see in a
debugger.

The fix: loop over `sorted(intervals)` (a new list), start `merged` empty, and always append a
**new** `[start, end]` list. Then the code only ever writes into lists it created itself, which
fixes the mutation and tuple reports together, and the empty case falls out for free.

## Code

```python
def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
```

## Complexity

O(n log n) for the sort, then one O(n) pass. Extra space O(n) for the sorted copy and the
result.

## Another way

Keep `cur_start, cur_end` in two plain variables and append `[cur_start, cur_end]` when a gap
appears (plus once after the loop). There is then no list to alias at all, at the cost of the
"don't forget the last block" step after the loop.

Then **prevent** it: the test file for this problem has one test per report. Keeping such
tests is the last step of the debugging loop (reproduce, isolate, fix, prevent).
