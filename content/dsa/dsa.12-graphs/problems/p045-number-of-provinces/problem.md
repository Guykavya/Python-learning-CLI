# Number of provinces

There are `n` cities. `is_connected` is an `n x n` matrix (a list of `n` lists): `is_connected[i][j] == 1` if city `i` and city `j` are joined by a direct road, `0` otherwise. The matrix is symmetric (`is_connected[i][j] == is_connected[j][i]`) and `is_connected[i][i] == 1`.

A **province** is a group of cities that are connected directly or through other cities, and not connected to any city outside the group.

Write `count_provinces(is_connected)` and return the number of provinces.

This is "count the connected components" (chapter section 5), with the graph given as an **adjacency matrix** (chapter section 2): the neighbours of city `i` are the `j` with `is_connected[i][j] == 1`. You can solve it with a search from every unvisited city, or with Union-Find (chapter section 9): start with `n` groups and unite every connected pair.

## Example

```python
>>> count_provinces([[1, 1, 0],
...                  [1, 1, 0],
...                  [0, 0, 1]])
2
>>> count_provinces([[1, 0, 0],
...                  [0, 1, 0],
...                  [0, 0, 1]])
3
>>> count_provinces([[1, 0, 1],
...                  [0, 1, 1],
...                  [1, 1, 1]])          # 0 and 1 are joined through 2
1
```

## Constraints

- `1 <= n <= 200`. Reading the whole matrix is `O(n^2)`, which is fine.

## Think about

Counting the 1s in the matrix tells you how many roads there are. Why does it not tell you the number of provinces?
