- Fixing `<` to `<=` and stopping there. Five reports, four separate causes; check every one.
- Replacing `intervals.sort()` with `sorted(intervals)` but keeping `merged = [intervals[0]]`
  (now of the sorted copy). `sorted` copies the outer list only; the pairs inside are still
  the caller's objects, so `last[1] = ...` still changes them.
- "Fixing" the mutation with `copy.deepcopy(intervals)` at the start. It works, but it hides the
  real rule (never write into objects you did not create) and copies everything up front.
- Using `last[1] = end` after sorting and assuming a later interval always ends later. Sorting
  by start says nothing about the ends.
- Adding `if not intervals: return []` but leaving the tuple crash. Building new lists fixes
  both.
- Returning tuples or the caller's tuples. The result must be new `[start, end]` lists.
