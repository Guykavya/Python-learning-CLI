**1. The bug.** `failed[user] >= 3` is a `d[key]` read on a `defaultdict(int)`. For every user
with no failures that read calls `int()`, **stores** `user: 0`, and then compares 0 with 3. After
the loop every user in the company is a key, so `len(failed)` counts all of them. Fixes (any two):
- read without creating: `if failed.get(user, 0) >= 3:`
- use a `Counter` instead: `failed = Counter()`; `failed[user]` returns 0 for a missing user
  **without** storing it;
- or count only real entries: `len([u for u, n in failed.items() if n > 0])`
  (works, but hides the real problem).

**2. Missing keys.**
- plain `dict`: `d[key]` raises `KeyError`. Nothing is stored.
- `defaultdict(int)`: calls the factory, **stores** `key: 0` and returns 0.
- `Counter`: returns 0 and does **not** store the key. (Only writes like `c[key] += 1` store it.)
`key in d` and `d.get(key)` never store anything, for all three.

**3. Choices.**
- a. `Counter`: built for counting, `Counter(words)` and `most_common(10)` (sorted, ties in first-seen order).
- b. `defaultdict(list)`: `index[word].append(line_no)` creates the empty list the first time,
  with no `if word not in index` check.
- c. plain `dict`: a typo like `cfg["prot"]` should raise `KeyError` right away; a defaultdict would
  silently invent a value and the bug would show up far away.
- d. `Counter`: multiset arithmetic. `not (Counter(note) - Counter(magazine))` is true when
  every letter is available often enough (the `-` operator drops counts that fall to zero or below).

**4. Return `dict(result)`.** The defaultdict is a building tool. If the caller gets it, an
innocent read like `result["typo"]` silently adds an entry instead of raising `KeyError`, and
`len(result)` or a JSON dump then contains keys nobody put there. Converting at the boundary gives
callers ordinary dict behaviour; the cost is one O(n) copy.

**Rule of thumb.** Counting → `Counter`. Grouping or accumulating into containers →
`defaultdict`. Everything else, and anything you hand to other code → plain `dict`. When you only
want to *look*, use `in` or `.get()` on any of them.
