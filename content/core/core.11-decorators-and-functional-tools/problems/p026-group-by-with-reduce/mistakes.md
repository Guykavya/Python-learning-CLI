- `groups.setdefault(k, []).append(item); return groups` inside the step. It works here, but it
  is not the "no mutation" style the problem asks for, and with a shared start value it leaks.
- A start value made outside the function, for example `EMPTY = {}` at module level and
  `reduce(step, items, EMPTY)` with a mutating step. The second call sees the first call's data.
- `merge_counts` that adds into its first argument: `total[k] = ...` on the caller's dict.
- Forgetting the start value: `reduce(merge_two, counts)` fails with `TypeError` when there are no dicts.
- `groups.get(k, []).append(item)` changes the list inside the OLD dict, because `{**groups}`
  copies only the outer dict, not the lists in it. Use `+ [item]` to make a new list.
