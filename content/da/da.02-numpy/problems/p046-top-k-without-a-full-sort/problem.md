# Top k without a full sort

Chapter section 15.3. Write `top_k(x, k)`: the **positions** of the `k` largest values of the 1-D array `x`, best first.

- Return an integer array of length `min(k, len(x))`; `x[result]` is in descending order. When several values are equal, any order among them is accepted.
- `k = 0` gives an empty integer array; `k >= len(x)` gives all positions, sorted by value (best first); `k < 0` raises `ValueError`.
- Do not sort all of `x`: use `np.argpartition` to bring the `k` best to one end in O(n), then sort only those `k`. The test switches `np.sort`, `np.argsort` and `np.lexsort` off for arrays with more than 10,000 elements (sorting the `k` winners is fine), and times your function on 1,000,000 values against a Python sort on the same machine.
- Do not change `x`.

## Example

```python
x = np.array([5, 9, 1, 7, 3, 8])
top_k(x, 3)
# array([1, 5, 3])      -> values 9, 8, 7
top_k(x, 0)
# array([], dtype=int64)
```
