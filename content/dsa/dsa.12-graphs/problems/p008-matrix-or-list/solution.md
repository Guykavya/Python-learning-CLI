## Approach

Turn every claim into a count. The memory formulas `V + 2E` and `V^2`, put next to each other with the numbers of the two examples, decide the first two questions. The operation costs follow from "what does each structure have to scan?".

## Model answer

See `answer.md`.

## What to check

- You gave numbers (700,000 against 10 billion; about 3.8 million against 4 million), not only "the list is smaller".
- You said **when** the matrix is good (dense graphs, constant-time edge tests, all-pairs tables), not only that it is bad.
- You explained the `O(V^2)` BFS by the row scans, not by the number of edges.
- You named the list of sets.

## Another way

Measure it: build both structures for `V = 2,000` with a few thousand random edges, time a BFS on each, and look at `sys.getsizeof` of a row. Then repeat with a dense graph and see the gap close.
