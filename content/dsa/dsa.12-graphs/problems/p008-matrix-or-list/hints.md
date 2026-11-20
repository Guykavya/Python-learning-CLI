## Hint 1

Count, do not guess: an adjacency list holds one entry per **end** of each edge (an undirected edge appears in two lists), plus one list per vertex. A matrix holds `V * V` cells, edges or not. Put the numbers of question 1 and question 2 into both formulas.

## Hint 2

For question 5, ask how BFS finds the neighbours of `u` in a matrix: it must look at every cell of row `u`, because it does not know where the `1`s are. How many rows does BFS look at, and how long is each?
