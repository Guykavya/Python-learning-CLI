## Model answer

**1. The road map.** An adjacency list stores one list per town and one entry per road **end**: about `V + 2E = 100,000 + 600,000 = 700,000` entries. A matrix always has `V^2 = 10^10` cells, ten billion, whatever the number of roads; even at one byte per cell that is 10 GB, and as Python lists it is far more. Only the list can be built.

**2. The dense group.** `V^2 = 4,000,000` cells against `V + 2E = 3,802,000` list entries: almost the same. When `E` is close to `V^2 / 2`, the matrix costs no more memory than the list, and it gives `O(1)` edge tests. For a dense graph a matrix is a fine choice (Floyd-Warshall, section 13, builds a full table anyway).

**3. Operations.**

| operation | adjacency list | adjacency matrix |
|---|---|---|
| is `u-v` an edge? | `O(degree(u))` | `O(1)` |
| neighbours of `u` | `O(degree(u))` | `O(V)` (scan a whole row) |
| visit every edge once | `O(V + E)` | `O(V^2)` |
| memory | `O(V + E)` | `O(V^2)` |

**4. Sparse and dense.** A graph is **sparse** when `E` is about the same size as `V` (a small multiple, `E = O(V)`), and **dense** when `E` is close to the maximum, about `V^2 / 2`. A grid is always sparse: each cell has at most 4 neighbours, so `E <= 2RC = O(V)`.

**5. BFS on a matrix.** BFS asks "who are the neighbours of `u`?" once for every vertex. With a matrix each question scans a row of `V` cells, even if `u` has two neighbours: `V * V = 4 * 10^8` cell reads. With a list the same BFS costs `V + 2E = 100,000` steps, about 4,000 times fewer. The matrix makes BFS `O(V^2)` instead of `O(V + E)`.

**6. Both.** A list of **sets** (`adj[u]` is a set): `v in adj[u]` is `O(1)` on average, iterating over `adj[u]` is `O(degree)`, and the memory is `O(V + E)`. If the neighbour **order** matters, keep a list next to the set (problem p004).

**Checklist: your answer should mention**
- [ ] list: about `V + 2E` entries (700,000); matrix: `V^2` cells (10 billion) for the road map
- [ ] for a dense graph the two sizes are similar, so a matrix is acceptable
- [ ] the matrix has `O(1)` edge tests but `O(V)` neighbour scans
- [ ] the list has `O(degree)` neighbours and `O(V + E)` traversal
- [ ] sparse means `E = O(V)`, dense means `E` near `V^2`; a grid is sparse (at most 4 neighbours per cell)
- [ ] BFS/DFS on a matrix is `O(V^2)` whatever `E` is
- [ ] a list of sets gives both fast edge tests and `O(V + E)` memory
