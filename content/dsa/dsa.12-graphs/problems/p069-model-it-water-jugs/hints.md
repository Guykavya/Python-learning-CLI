## Hint 1

From `(0, 0)`: fill A gives `(3, 0)`, fill B gives `(0, 5)`; emptying or pouring changes nothing, so those give `(0, 0)`, already seen. The queue is now `(3, 0), (0, 5)`. From `(3, 0)`: fill B gives `(3, 5)`, and pour A into B moves all 3 litres: `(0, 3)`.

## Hint 2

From `(0, 5)`, pour B into A moves `min(5, 3 - 0) = 3` litres: `(3, 2)`. From `(3, 2)`, empty A gives `(0, 2)`; from `(0, 2)`, pour B into A gives `(2, 0)`. Keep going in queue order; the first state with 4 litres in either jug that is taken out of the queue ends the search.
