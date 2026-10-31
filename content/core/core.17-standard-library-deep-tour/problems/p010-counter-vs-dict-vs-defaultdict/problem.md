# Explain: Counter, defaultdict or a plain dict?

All three are dicts (`Counter` and `defaultdict` are subclasses of `dict`). They differ in what
happens on a **missing key** and in the extra tools they bring. Choosing well removes whole
classes of bugs.

A teammate wrote this report of failed logins per user:

```python
from collections import defaultdict

failed = defaultdict(int)
for user, ok in events:            # events: list of (user, ok: bool)
    if not ok:
        failed[user] += 1

for user in all_users:             # every user in the company
    if failed[user] >= 3:
        print("lock", user)

print(len(failed), "users had failures")   # always prints the number of ALL users
```

In `answer.md` (about 250 to 400 words), explain:

1. **The bug.** Why does the last line print the number of *all* users, not of users with
   failures? Give two different one-line fixes.
2. **Missing keys.** What does `d[key]` do on a missing key for a plain `dict`, a
   `defaultdict(int)` and a `Counter`? Which of them **stores** the key?
3. **Choose a container** for each task and give the reason in one sentence:
   - a. Count words in a file and print the 10 most common.
   - b. Build an index: word → list of line numbers where it appears.
   - c. Settings loaded from a config file and passed around the program, where a typo in a key name must fail loudly.
   - d. Compare the letters of two words to see whether one can be built from the other's letters (a ransom-note check).
4. **Returning results.** Why is it good practice for a function that builds a `defaultdict`
   internally to `return dict(result)`?

**Example** of the level of detail expected for one part:

> 3a. `Counter`: counting is its job, `Counter(words)` does it in one line, and
> `most_common(10)` gives the top ten already sorted.
