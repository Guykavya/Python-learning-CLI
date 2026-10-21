- Updating cells in place.
- Using `new = grid.copy()` or `new = grid[:]` and writing into it: rows are shared, so it is
  still in place.
- Wrapping around the edges instead of treating outside cells as dead.
- Counting the cell itself as its own neighbour.
