# Why a list cannot be a dict key

This works:

```python
seats = {(2, 5): "Asha"}
print(seats[(2, 5)])
```

This fails with `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')`:

```python
seats = {[2, 5]: "Asha"}
```

Explain in your own words, in `answer.md`:

1. How a dict finds a key quickly. What is a hash, and what does the dict do with it?
2. What "hashable" means: the two rules a key's hash must follow.
3. Walk through what would go **wrong** if Python allowed the list `[2, 5]` as a key and you
   then appended to that list.
4. Why the tuple `(2, 5)` is safe, and why the tuple `(2, [5])` is **not** hashable.
5. What you would use as a key for "the pair of people Asha and Ravi" if the order of the two
   names should not matter.

Use small diagrams or examples if they help.
