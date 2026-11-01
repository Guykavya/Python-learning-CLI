- `groupby` on unsorted data when you wanted "group everything with the same key". It only joins
  neighbours. Here that is what we want for runs; for `group_by_length` use `defaultdict`.
- Using `groupby` results after moving on to the next group: the group is a one-time iterator;
  turn it into a list (or count it) right away.
- Keeping `seen` as a list while switching to `deque`. The queue is faster but each check is still O(n).
- Returning the `defaultdict` itself: later lookups of a missing key silently create entries.
  `dict(groups)` is the safe return value.
- `@cache` on a function with unhashable arguments (lists) raises `TypeError`.
- `Counter(text.split())` without `.lower()`: "The" and "the" become two words.
