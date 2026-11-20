## Hint 1

For question 1, go around the cycle: red, blue, red, blue, ... After `L` steps you are back at the start. Which colour does the walk say the start must have after an odd number of steps?

For question 2: if `u` is in layer `k` and `v` is a neighbour of `u`, then `dist(v) <= k + 1` (one more step), and by the same argument `dist(u) <= dist(v) + 1`. What does that leave for `dist(v)`?

## Hint 2

For question 4: the path from `a` (layer `j`) down the BFS tree to `u` (layer `k`) has `k - j` edges; the same for `v`. The two tree paths share only `a` (that is where they first meet). Add the edge `u - v`: the cycle has `(k - j) + (k - j) + 1` edges. Which numbers of the form `2m + 1` are even?

For question 7: after you colour a vertex red with three colours, its neighbour can be blue **or** green. What happens to the number of possibilities as you go?
