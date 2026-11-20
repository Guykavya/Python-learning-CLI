# Knight moves

A chess knight on an `n x n` board moves in an "L": two squares in one direction and one square at a right angle, so from `(r, c)` it can go to the 8 squares `(r ± 2, c ± 1)` and `(r ± 1, c ± 2)`, as long as they are on the board.

Write `knight_moves(n, start, target)`. `start` and `target` are `(row, col)` tuples with `0 <= row, col < n`. Return the **smallest number of moves** that takes the knight from `start` to `target`, or `-1` if it can never get there.

Nobody gives you the graph: the squares are the vertices and the legal moves are the edges, generated on the fly. This is BFS on an implicit graph (chapter sections 2 and 3).

## Example

```python
>>> knight_moves(8, (0, 0), (1, 2))
1
>>> knight_moves(8, (0, 0), (7, 7))
6
>>> knight_moves(8, (0, 0), (1, 1))
4
>>> knight_moves(3, (0, 0), (1, 1))       # the centre of a 3x3 board has no moves at all
-1
>>> knight_moves(5, (2, 2), (2, 2))
0
```

## Constraints

- `1 <= n <= 300`. `O(n^2)` time per call.

## Think about

On an endless board, `(0, 0) -> (1, 1)` takes only 2 moves. Why does it take 4 on a real board? Which line of your code makes the difference? And why must the search be BFS, not DFS?
