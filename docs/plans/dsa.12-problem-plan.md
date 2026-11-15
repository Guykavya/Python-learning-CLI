# Problem plan: dsa.12 Graphs (70 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.12.p001`…`p070`.
**Mix:** 18 drill, 31 applied, 15 deep, 6 challenge. Kinds: 57 code, 9 trace, 4 explain. **assessment:** explain = p008, trace = p020, fix = p041, build = p070.
Graph input style: `n` and an edge list `[(u, v)]` or `[(u, v, w)]`, nodes `0..n-1`; grids as list of strings. Tests compare with a brute-force reference (Floyd-Warshall for shortest paths, simple DFS for connectivity) on random graphs, fixed seed. Where several answers are valid (topological order, a path), the test **validates** the answer instead of comparing it. Performance tests use 10**5 nodes/edges and an iterative DFS, so recursion-limit failures give the message "use an iterative DFS".

## A. Representations (Ch. 2)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | Edge list to adjacency list | drill | code | undirected and directed; self loops; isolated nodes present |
| 2 | Degrees | drill | code | in/out degree dicts; handshake check in the test |
| 3 | Adjacency matrix and back | drill | code | |
| 4 | Is there an edge? | drill | code | matrix vs list cost explained in `solution.md` |
| 5 | Grid as a graph: neighbours | drill | code | 4 and 8 directions, borders |
| 6 | Weighted adjacency list | drill | code | parallel edges keep the smaller weight |
| 7 | Transpose a directed graph | applied | code | |
| 8 | Matrix or list? | drill | explain | graded by terms ("dense", "sparse", "V^2") |

## B. BFS and DFS (Ch. 3–5)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 9 | BFS order | drill | code | neighbours visited in adjacency order; unreachable nodes absent |
| 10 | Shortest path length (unweighted) | drill | code | `-1` if unreachable; same node = 0 |
| 11 | Shortest path itself | applied | code | validated: consecutive nodes are edges, length is minimal |
| 12 | DFS order (recursive) | drill | code | |
| 13 | DFS order (iterative) | applied | code | 10**5-node chain works |
| 14 | Trace BFS | drill | trace | `⚠ HAND-TRACE` queue and `dist` after each pop on a 7-node graph |
| 15 | Trace DFS with entry/exit times | applied | trace | `⚠ HAND-TRACE` enter and exit numbers for each node |
| 16 | Connected components count | drill | code | isolated nodes count |
| 17 | Largest component | applied | code | |
| 18 | Number of islands | drill | code | 1x1, all water, 100x100 |
| 19 | Max area of an island | applied | code | |
| 20 | Flood fill | applied | trace | `⚠ HAND-TRACE` the final grid and the visit order for a 4x4 grid |
| 21 | Surrounded regions | applied | code | border flood from the edges |
| 22 | Pacific Atlantic water flow | deep | code | two multi-source searches |
| 23 | Word ladder | deep | code | BFS on words; validated length; no path → 0 |
| 24 | Open the lock | applied | code | 4-wheel BFS; deadends |
| 25 | Clone a graph | applied | code | no shared nodes; cycles preserved |
| 26 | Shortest bridge | challenge | code | DFS to mark, then multi-source BFS |
| 27 | Nearest 0 (multi-source BFS) | applied | code | 01-matrix |
| 28 | Knight moves | applied | code | minimum moves on an 8x8 board |

## C. Cycles, topological order, bipartite (Ch. 6–8)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 29 | Cycle in an undirected graph | drill | code | parent trap: edge back to the parent is not a cycle; parallel edges are a cycle |
| 30 | Cycle in a directed graph | applied | code | three colours; self loop |
| 31 | Topological order (Kahn) | applied | code | validated order; cycle → `[]` |
| 32 | Topological order (DFS) | applied | code | same validation |
| 33 | Course schedule | drill | code | can all be finished? |
| 34 | Course schedule II | applied | code | any valid order |
| 35 | Trace Kahn's algorithm | applied | trace | `⚠ HAND-TRACE` queue and in-degrees after each step |
| 36 | Alien dictionary | challenge | code | derive order from sorted words; invalid prefix case |
| 37 | Parallel courses (longest chain) | deep | code | levels of topological sort |
| 38 | Is the graph bipartite? | drill | code | disconnected graphs; odd cycle |
| 39 | Possible bipartition | applied | code | dislikes graph |
| 40 | Colouring a bipartite graph | applied | code | returns a validated colouring |
| 41 | Fix the cycle detector | applied | code | `assessment = "fix"`; given a DFS that reports a cycle for a diamond graph (shared node, no cycle) |
| 42 | Why do two colours suffice? | deep | explain | odd cycle argument; graded by terms |

## D. Union-Find (Ch. 9)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 43 | DSU class | applied | code | `find/union/connected/count`; path compression; random ops vs BFS model |
| 44 | Redundant connection | applied | code | last edge that makes a cycle |
| 45 | Number of provinces | drill | code | matrix input |
| 46 | Accounts merge | deep | code | emails sorted; names |
| 47 | Trace union by size | drill | trace | `⚠ HAND-TRACE` parent and size arrays after 6 unions |
| 48 | Number of islands II (online) | challenge | code | adding land cells one at a time |
| 49 | Why is DSU nearly O(1)? | deep | explain | path compression + union by size; graded by terms |

## E. Shortest paths (Ch. 10–14)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 50 | Dijkstra | applied | code | distances list; unreachable `inf`; compare with Floyd–Warshall |
| 51 | Network delay time | applied | code | time for all nodes or `-1` |
| 52 | Path with minimum effort | deep | code | grid; max-edge path |
| 53 | Cheapest flights within K stops | deep | code | Bellman-Ford style layers |
| 54 | Trace Dijkstra | applied | trace | `⚠ HAND-TRACE` heap contents and `dist` after each pop |
| 55 | Why Dijkstra fails with negative edges | deep | explain | give a 3-node counterexample; the test runs the answer through both algorithms |
| 56 | 0-1 BFS | applied | code | deque; compare with Dijkstra |
| 57 | Bellman-Ford with negative cycle | deep | code | returns `None` if a negative cycle is reachable |
| 58 | Floyd-Warshall | applied | code | loop order trap: `k` outermost (message) |
| 59 | Arbitrage? (negative cycle in logs) | challenge | code | exchange rates; tolerance |
| 60 | Trace Bellman-Ford rounds | applied | trace | `⚠ HAND-TRACE` distance array after each round |

## F. MST, SCC, bridges, modelling (Ch. 15–19)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 61 | Kruskal | applied | code | total weight; disconnected → `None`; compare with Prim |
| 62 | Prim | applied | code | |
| 63 | Min cost to connect all points | deep | code | Manhattan; complete graph |
| 64 | Trace Kruskal | applied | trace | `⚠ HAND-TRACE` sorted edges, accepted/rejected |
| 65 | Strongly connected components | deep | code | Kosaraju or Tarjan; validated partition; 10**5 nodes iterative |
| 66 | Critical connections (bridges) | challenge | code | brute-force: remove each edge and test connectivity |
| 67 | Articulation points | challenge | code | brute-force compare |
| 68 | Evaluate division (weighted graph) | deep | code | |
| 69 | Model it: reachability puzzle | deep | trace | `⚠ HAND-TRACE` water jug puzzle as a graph: list of reachable states and the shortest path |
| 70 | Build a graph library | deep | code | `assessment = "build"`; class `Graph` with `add_edge`, `bfs`, `dfs`, `components`, `topo`, `shortest` and tests against the earlier references |

## Counts
Tiers about 23/23/17/7. Traces: 14, 15, 20, 35, 47, 54, 60, 64, 69 explicit; add p10, p38, p56 as hand-computation variants for 12. Explain: 8, 42, 49, 55 plus p4 and p29 as written variants for 6. One assessment of each kind.

## Real-site problems (`external.toml`)
LeetCode `number-of-islands`, `max-area-of-island`, `clone-graph`, `surrounded-regions`, `pacific-atlantic-water-flow`, `word-ladder`, `open-the-lock`, `01-matrix`, `shortest-bridge`, `course-schedule`, `course-schedule-ii`, `alien-dictionary`, `is-graph-bipartite`, `possible-bipartition`, `redundant-connection`, `number-of-provinces`, `accounts-merge`, `network-delay-time`, `path-with-minimum-effort`, `cheapest-flights-within-k-stops`, `min-cost-to-connect-all-points`, `critical-connections-in-a-network`, `evaluate-division`; CSES 1192, 1193, 1194, 1666, 1667, 1668, 1669, 1671, 1672, 1195, 1197, 1202, 1675, 1683, 1682, 1678 (graph section) to verify. Ids unverified.
