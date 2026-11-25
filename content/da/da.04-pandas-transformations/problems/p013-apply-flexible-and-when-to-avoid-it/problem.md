# `apply`: flexible, and when to avoid it

Chapter sections 4.3 and 12.2. A colleague's notebook uses `groupby(...).apply` for everything:

```python
total = lines.groupby("category").apply(lambda d: d["revenue"].sum())
z = lines.groupby("category")["revenue"].transform(lambda s: (s - s.mean()) / s.std())
top2 = lines.groupby("category").apply(lambda d: d.nlargest(2, "revenue"))
```

On the 6,000-line table it is fast enough. On a table with 5,000 customers as groups the same code takes many times
longer. Explain in `answer.md`, in about 200 to 300 words:

1. What does `groupby(...).apply(func)` do for each group, and why does its cost grow with the **number of groups**?
2. Give the faster replacement for **each** of the three lines above, and say why it is faster.
3. Name one pandas 3 surprise of `apply` on groups (Ch. 4.3), and how a function can still get the group key.
4. When is `apply` still the right tool, and what do you do before replacing working code with a "faster" version?

## Example

A start: "`apply` hands each group's sub-table to my Python function and glues the results together. That means one
Python call, and one new small DataFrame, per group..."
