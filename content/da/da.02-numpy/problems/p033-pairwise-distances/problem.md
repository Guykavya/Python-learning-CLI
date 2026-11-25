# Pairwise distances

Chapter section 11.7. Write `pairwise_distances(a, b)`: for `n` points `a` of shape `(n, d)` and `m` points `b` of shape `(m, d)`, return the `(n, m)` table of Euclidean distances, entry `[i, j]` = distance from `a[i]` to `b[j]` = `sqrt(sum over k of (a[i, k] - b[j, k]) ** 2)`.

- Use broadcasting: no Python loop over the pairs. The test times your function on 2,000 × 2,000 points in 3-D and compares it, on the same machine, with the broadcast version of Ch. 11.7; a double loop over the pairs is far too slow.
- The result is `float64`. Lists are allowed as input. `n` or `m` may be 1.
- The distance from a point to an identical point must be exactly `0` (never `nan`).
- If the two point sets do not have the same number of coordinates `d`, raise `ValueError`.

## Example

```python
a = np.array([[0.0, 0.0], [3.0, 4.0]])
b = np.array([[0.0, 0.0], [6.0, 8.0], [0.0, 5.0]])
pairwise_distances(a, b)
# array([[ 0.        , 10.        ,  5.        ],
#        [ 5.        ,  5.        ,  3.16227766]])
```
