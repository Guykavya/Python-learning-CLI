- Forgetting to remove the old phone from `by_phone` on `update` or `delete`, so a freed number
  still "belongs" to someone.
- Rejecting `update ravi 97000` when 97000 is already ravi's own number. Only a **different**
  owner is a conflict.
- Sorting with plain `sorted()`, which puts all capitalised names first.
- Searching `by_name.values()` for the `phone` command: correct, but O(n) per lookup.
