**1. What groupby groups.** `groupby` only groups **neighbours**: items that come one after another
with the same key. It walks the input once and starts a new group every time the key changes. In
`sales` the keys are `tea, coffee, tea, juice, coffee`. No two neighbours share a key, so every item
is its own group, and `tea` appears twice.

**2. Why sorting fixes it.** After `sorted(sales)` all items with the same key sit next to each other,
so each key forms exactly one group: `coffee 9`, `juice 1`, `tea 5`. The cost: sorting takes
O(n log n) time, and `sorted` builds a full list in memory, so the pipeline is not lazy any more.
If the data already arrives grouped (log lines in time order grouped by minute, or rows sorted by
customer), sorting is not needed and `groupby` stays lazy and uses O(1) memory.

**3. Why the lists are empty.** `groupby` is one iterator over the input, and each `group` is a small
view that reads from **that same shared iterator**. It is not a stored list. When the dict
comprehension asks `groupby` for the next key, `groupby` must skip past the rest of the current
group, so those items are used up. By the time we call `list(g)`, the items are gone and every
group is empty.

**4. The fix.** Turn each group into a list *before* moving on:

```python
saved = {name: list(group) for name, group in groupby(sorted(sales), key=lambda s: s[0])}
```

**5. When a dict is better.** If the data is not sorted and I only need totals or counts, one pass
with a dict is O(n) time and does not need a sort. It also works on an infinite or very long
stream (memory is one entry per key). `groupby` is the better tool when the data is already grouped,
or when I need the items of each group in order.
