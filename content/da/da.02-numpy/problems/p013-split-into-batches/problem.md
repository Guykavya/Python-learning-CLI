# Split into batches

Chapter sections 5.6 and 6.1. Training and reporting code often walks through data in **batches**. Write
`batches(x, size)` that returns a Python **list** of arrays:

- each batch holds `size` consecutive items of `x` (rows, if `x` is 2-D), in order;
- the **last** batch may be shorter; if `size >= len(x)` there is one batch with everything;
- an empty `x` gives an empty list `[]`;
- every batch is a **view** of `x` (no copies);
- `size <= 0` raises `ValueError`.

A short Python loop over the *batches* is fine (there are only `len(x) / size` of them); the elements inside a batch
must not be copied.

## Example

```python
x = np.arange(10)
[b.tolist() for b in batches(x, 4)]    # [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
[b.tolist() for b in batches(x, 20)]   # [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
batches(np.arange(0), 3)               # []
```
