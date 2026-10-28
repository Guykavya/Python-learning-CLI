## Approach

Two separate ideas explain the two surprises. First, `groupby` is a one-pass tool that only looks at
the **previous** key, so it can only group items that are next to each other. Second, the groups
are lazy views into one shared iterator, so a group must be used **before** the next one is
requested.

## Model answer

See `answer.md`.

## Complexity

`groupby` itself: O(n) time, O(1) memory. With `sorted` first: O(n log n) time, O(n) memory.
A dict of totals: O(n) time, O(k) memory for k keys.

## Another way

Think of `groupby` like the Unix command `uniq`: it only merges lines that are next to each other,
which is why people write `sort | uniq`.
