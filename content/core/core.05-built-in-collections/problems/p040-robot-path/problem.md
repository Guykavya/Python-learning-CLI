# Robot path

A robot starts at `(0, 0)`. Read one line of moves made of the letters `U`, `D`, `L`, `R`
(up is `y + 1`, down is `y - 1`, left is `x - 1`, right is `x + 1`). The line may be empty.

Print:

```
Visited: <number of distinct cells visited, including the start>
Revisits: <number of moves that landed on a cell already visited>
Final: (<x>, <y>)
```

**Example**

Input:
```
URDLUU
```
Output:
```
Visited: 5
Revisits: 2
Final: (0, 2)
```

The path is (0,0), (0,1), (1,1), (1,0), (0,0), (0,1), (0,2). The 4th move lands on (0,0) and
the 5th on (0,1), both seen before, so there are 2 revisits and 5 distinct cells.

The tests include 200,000 moves, so a list of visited cells is too slow.
