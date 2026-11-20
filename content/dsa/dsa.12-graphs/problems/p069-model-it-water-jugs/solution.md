## Approach

Run the BFS by hand: a queue, a set of seen states, and the six moves in order. The goal is tested when a state is dequeued.

## Expected output

```text
(0, 0) -> new [(3, 0), (0, 5)]
(3, 0) -> new [(3, 5), (0, 3)]
(0, 5) -> new [(3, 2)]
(3, 5) -> new []
(0, 3) -> new [(3, 3)]
(3, 2) -> new [(0, 2)]
(3, 3) -> new [(1, 5)]
(0, 2) -> new [(2, 0)]
(1, 5) -> new [(1, 0)]
(2, 0) -> new [(2, 5)]
(1, 0) -> new [(0, 1)]
(2, 5) -> new [(3, 4)]
(0, 1) -> new [(3, 1)]
found (3, 4) after 6 moves
[(0, 0), (0, 5), (3, 2), (0, 2), (2, 0), (2, 5), (3, 4)]
```


## Why

The queue after each line (front first): `(3,0) (0,5)`, then `(0,5) (3,5) (0,3)`, then `(3,5) (0,3) (3,2)`, and so on. Two branches grow side by side: one starts with "fill A" (`(3,0)`, `(0,3)`, `(3,3)`, `(1,5)`, `(1,0)`, `(0,1)`, `(3,1)`), the other with "fill B" (`(0,5)`, `(3,2)`, `(0,2)`, `(2,0)`, `(2,5)`, `(3,4)`). The "fill B" branch reaches 4 litres first. `(3, 4)` is discovered while handling `(2, 5)`, but the search only stops when it is **taken out**, after `(0, 1)` has been handled (which discovers `(3, 1)`).

The path, as instructions: fill B `(0,5)`, pour B into A `(3,2)`, empty A `(0,2)`, pour B into A `(2,0)`, fill B `(2,5)`, pour B into A `(3,4)`: B holds 4 litres after 6 moves. BFS explores states in order of the number of moves, so no solution with fewer moves exists.

The search discovered 15 states (all keys of `parent`, `(3, 1)` included). Not every pair is reachable: after every move at least one jug is either empty or full, so for example `(1, 1)` or `(2, 3)` can never occur.

## Another way

Count without the program: the amounts you can measure are combinations `3x + 5y`; 4 = `3 * 3 - 5` (fill A three times, empty B once), which is the other branch: `(3,0) (0,3) (3,3) (1,5) (1,0) (0,1) (3,1) (0,4)`: 8 moves. BFS proves that 6 is the minimum.
