# Nearest neighbour in chunks

Chapter sections 11.7 and 17.4 (processing in chunks). Write `nearest_distance(points, chunk=250)`: for every point of `points` (shape `(n, d)`), the Euclidean distance to its nearest **other** point.

- Return a `float64` array of shape `(n,)`. A point's distance to itself does not count; two identical points are each other's nearest neighbour at distance `0`.
- `n < 2` (no other point exists) or `chunk < 1` raise `ValueError`.
- **Memory is the point of this problem.** The test uses `n = 12,000` points. The full table of distances alone has 12,000 × 12,000 float64 values = 1.15 GB, and the 3-D difference array behind it twice that. Where the course runner caps memory at 1 GiB (not on Windows) that is a `MemoryError`. Process the points `chunk` rows at a time: compare one block of rows with **all** points, keep each row's minimum, move on. A block of 250 rows needs 250 × 12,000 × 2 floats = 48 MB.
- The test also measures your peak memory with `tracemalloc` on 6,000 points with `chunk=50` (this works on every system): it must stay below 25 MB, so your function must really use the `chunk` it is given.
- Do not change the caller's array.

## Example

```python
pts = np.array([[0.0, 0.0], [3.0, 4.0], [6.0, 8.0], [0.0, 5.0]])
nearest_distance(pts, chunk=3)
# array([5.        , 3.16227766, 5.        , 3.16227766])
```

Point 0 is 5 away from points 1 and 3; point 1 is closest to point 3 (√10); point 2 is closest to point 1. With `chunk=3` the first block holds rows 0–2 and the second block row 3 only: the self-distances to ignore sit at different columns in each block.
