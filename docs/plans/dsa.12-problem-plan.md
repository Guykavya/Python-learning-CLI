# Problem plan: dsa.12 Graphs (70 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.12.p001`…`p070`. Function style (`from solution import f`).
**Mix:** 18 drill, 31 applied, 15 deep, 6 challenge. Kinds: 57 code (incl. fix p041 and build p070), 9 trace, 4 explain. **assessment:** explain = p008, trace = p020, fix = p041, build = p070.
Graph input style: `n` and an edge list `[(u, v)]` or `[(u, v, w)]`, nodes `0..n-1`; grids as list of strings. Tests compare with a brute-force reference (Floyd-Warshall for shortest paths, simple DFS for connectivity) on random graphs, fixed seed. Where several answers are valid (topological order, a path), the test **validates** the answer instead of comparing it. Performance tests use 10**5 nodes/edges and an iterative DFS, so recursion-limit failures give the message "use an iterative DFS".

## Conventions (pin these in every statement that needs them)
- **Adjacency order = edge-list order.** For an undirected edge `(u, v)` append `v` to `adj[u]` and `u` to `adj[v]`, in the order the edges are listed. BFS/DFS orders that tests compare exactly (p009, p012, p013, p014, p015, p020) depend on this; say it in the statement.
- p013's iterative DFS must give the **same order as the recursive one** (push neighbours reversed, skip a vertex that is already visited when it is popped); the chapter's "DFS with a stack" section shows the trap.
- Recursive solutions are only tested on small graphs (pytest already uses ~34 frames; keep recursive depth tests at 800 or less). Big cases (10**5) are for problems that ask for an iterative version.
- Every test file is **self-contained**: the engine copies only `solution.py`, `test_solution.py`, `conftest.py` and `fixtures/`, so brute-force references (Floyd-Warshall, BFS models, Prim for Kruskal) are written inside the test file.
- Grid problems that change a grid return a **new** list of strings (strings cannot be edited in place).
- Unreachable distance: `float("inf")` for distance lists (p050, p057, p058), `-1` where the statement says so (p010, p051).
- Explain problems are self-rated against `answer.md` (a checklist of terms); nothing is machine-graded.
- Trace problems: the code is in `problem.md`; `expected.txt` comes from running that exact code and is then checked by hand.

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
| 8 | Matrix or list? | drill | explain | `answer.md` checklist: "dense", "sparse", "V^2 memory", "edge test O(1) vs O(degree)", "iterate neighbours" |

## B. BFS and DFS (Ch. 3–5)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 9 | BFS order | drill | code | neighbours visited in adjacency order; unreachable nodes absent |
| 10 | Shortest path length (unweighted) | drill | code | `-1` if unreachable; same node = 0 |
| 11 | Shortest path itself | applied | code | validated: consecutive nodes are edges, length is minimal |
| 12 | DFS order (recursive) | drill | code | small graphs only |
| 13 | DFS order (iterative) | applied | code | same order as p012; 10**5-node chain works |
| 14 | Trace BFS | drill | trace | `⚠ HAND-TRACE` queue and `dist` after each pop on a 7-node graph |
| 15 | Trace DFS with entry/exit times | applied | trace | `⚠ HAND-TRACE` enter and exit numbers for each node |
| 16 | Connected components count | drill | code | isolated nodes count |
| 17 | Largest component | applied | code | |
| 18 | Number of islands | drill | code | 1x1, all water, 100x100 (iterative or the test says "use an iterative DFS") |
| 19 | Max area of an island | applied | code | |
| 20 | Flood fill | applied | trace | `assessment = "trace"`; `⚠ HAND-TRACE` the final grid and the visit order for a 4x4 grid, BFS code in `problem.md` |
| 21 | Surrounded regions | applied | code | border flood from the edges |
| 22 | Pacific Atlantic water flow | deep | code | two multi-source searches; result sorted |
| 23 | Word ladder | deep | code | BFS on words; length counts words (LeetCode style); no path → 0 |
| 24 | Open the lock | applied | code | 4-wheel BFS; deadends; start is a deadend → -1 |
| 25 | Clone a graph | applied | code | no shared nodes; cycles preserved (`Node` class in starter and reference) |
| 26 | Shortest bridge | challenge | code | DFS to mark, then multi-source BFS |
| 27 | Nearest 0 (multi-source BFS) | applied | code | 01-matrix; compare with brute force |
| 28 | Knight moves | applied | code | minimum moves on an n×n board; unreachable on tiny boards → -1 |

## C. Cycles, topological order, bipartite (Ch. 6–8)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 29 | Cycle in an undirected graph | drill | code | parent trap: edge back to the parent is not a cycle; parallel edges are a cycle |
| 30 | Cycle in a directed graph | applied | code | three colours; self loop |
| 31 | Topological order (Kahn) | applied | code | validated order; cycle → `[]` |
| 32 | Topological order (DFS) | applied | code | same validation; iterative for 10**5 |
| 33 | Course schedule | drill | code | can all be finished? |
| 34 | Course schedule II | applied | code | any valid order |
| 35 | Trace Kahn's algorithm | applied | trace | `⚠ HAND-TRACE` queue and in-degrees after each step |
| 36 | Alien dictionary | challenge | code | derive order from sorted words; any valid order of all letters; invalid (longer word before its own prefix, or a cycle) → `""`; test validates |
| 37 | Parallel courses (longest chain) | deep | code | levels of topological sort (rounds); cycle → -1 |
| 38 | Is the graph bipartite? | drill | code | disconnected graphs; odd cycle |
| 39 | Longest path in a DAG | applied | code | Ch. 7 "Dynamic programming on a DAG": weighted DAG, longest path from a source (unreachable → `None`) and the number of paths mod 10**9+7; compare with brute-force path enumeration on small DAGs |
| 40 | Colouring a bipartite graph | applied | code | returns a validated colouring or `None`; dislike-pairs example (the old "possible bipartition") in the statement |
| 41 | Fix the cycle detector | applied | code | `assessment = "fix"`; given a directed DFS with ONE visited set that reports a cycle for a diamond graph (shared node, no cycle) |
| 42 | Why do two colours suffice? | deep | explain | odd cycle argument; `answer.md` checklist |

## D. Union-Find (Ch. 9)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 43 | DSU class | applied | code | `find/union/connected/count`; path compression; random ops vs BFS model; 10**5 unions on a chain do not hit the recursion limit (iterative find) |
| 44 | Redundant connection | applied | code | last edge that makes a cycle |
| 45 | Number of provinces | drill | code | matrix input |
| 46 | Accounts merge | deep | code | each account = name followed by its emails sorted; accounts sorted by (name, first email) |
| 47 | Trace union by size | drill | trace | `⚠ HAND-TRACE` parent and size arrays after 6 unions (tie rule pinned in the code) |
| 48 | Number of islands II (online) | challenge | code | adding land cells one at a time; a repeated cell does not change the count |
| 49 | Why is DSU nearly O(1)? | deep | explain | path compression + union by size; `answer.md` checklist |

## E. Shortest paths (Ch. 10–14)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 50 | Dijkstra | applied | code | distances list; unreachable `inf`; compare with Floyd–Warshall |
| 51 | Network delay time | applied | code | time for all nodes or `-1` |
| 52 | Path with minimum effort | deep | code | grid; max-edge path |
| 53 | Cheapest flights within K stops | deep | code | Bellman-Ford style layers; the copy trap (Ch. 12) |
| 54 | Trace Dijkstra | applied | trace | `⚠ HAND-TRACE` heap contents (sorted) and `dist` after each pop, including one stale entry that is skipped |
| 55 | Why Dijkstra fails with negative edges | deep | explain | give a 3-node counterexample; self-rated: `answer.md` holds a counterexample and a short script the learner may run to see both algorithms disagree |
| 56 | 0-1 BFS | applied | code | deque; compare with Dijkstra |
| 57 | Bellman-Ford with negative cycle | deep | code | returns `None` if a negative cycle is reachable from the source (an unreachable one does not count) |
| 58 | Floyd-Warshall | applied | code | loop order trap: `k` outermost (message) |
| 59 | Arbitrage? (negative cycle in logs) | challenge | code | exchange rates; tolerance |
| 60 | Trace Bellman-Ford rounds | applied | trace | `⚠ HAND-TRACE` distance array after each round (edge order fixed in the code) |

## F. MST, SCC, bridges, modelling (Ch. 15–19)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 61 | Kruskal | applied | code | total weight; disconnected → `None`; compare with a Prim inside the test |
| 62 | Prim | applied | code | |
| 63 | Min cost to connect all points | deep | code | Manhattan; complete graph (dense Prim, Ch. 15) |
| 64 | Trace Kruskal | applied | trace | `⚠ HAND-TRACE` sorted edges, accepted/rejected |
| 65 | Strongly connected components | deep | code | Kosaraju or Tarjan; validated partition; 10**5 nodes iterative |
| 66 | Critical connections (bridges) | challenge | code | brute-force: remove each edge and test connectivity; parallel edges are not bridges (Ch. 17 trap) |
| 67 | Articulation points | challenge | code | brute-force compare |
| 68 | Evaluate division (weighted graph) | deep | code | unknown variable → -1.0; float tolerance |
| 69 | Model it: reachability puzzle | deep | trace | `⚠ HAND-TRACE` water jug puzzle as a graph: list of reachable states and the shortest path |
| 70 | Build a graph library | deep | code | `assessment = "build"`; class `Graph` with `add_edge`, `bfs`, `dfs`, `components`, `topo`, `shortest`; the test file holds its own brute-force models (it cannot import other problems) |

## Counts
Tiers 18 drill / 31 applied / 15 deep / 6 challenge. Traces: p014, p015, p020, p035, p047, p054, p060, p064, p069 (9). Explain: p008, p042, p049, p055 (4). Fix: p041. Build: p070. Everything else is code (57).

## Changes against the first draft (made 2026-11-16)
1. The old count line (23/23/17/7, extra trace/explain variants) did not match the table; replaced.
2. p039 "Possible bipartition" duplicated p038/p040; it became "Longest path in a DAG" (Ch. 7 DP on a DAG had no problem). The dislike-pairs story moved into p040's statement.
3. p055 said "the test runs the answer", and p008/p042/p049 "graded by terms": explain problems are self-rated.
4. p070 said "tests against the earlier references": tests cannot import other problems, so they hold their own models.
5. Pinned: adjacency order, iterative DFS order equal to recursive, return types for unreachable, grid problems return new lists, small-only recursive tests.
6. `alien-dictionary` (LeetCode Premium) removed from the real-site list.

## Real-site problems (`external.toml`)
Free LeetCode only, slugs from memory and unverified: `number-of-islands`, `max-area-of-island`, `clone-graph`, `surrounded-regions`, `pacific-atlantic-water-flow`, `word-ladder`, `open-the-lock`, `01-matrix`, `shortest-bridge`, `course-schedule`, `course-schedule-ii`, `is-graph-bipartite`, `possible-bipartition`, `redundant-connection`, `number-of-provinces`, `accounts-merge`, `network-delay-time`, `path-with-minimum-effort`, `cheapest-flights-within-k-stops`, `min-cost-to-connect-all-points`, `critical-connections-in-a-network`, `evaluate-division`; CSES 1192, 1193, 1194, 1666, 1667, 1668, 1669, 1671, 1672, 1195, 1197, 1202, 1675, 1683, 1682, 1678 (graph section, ids from memory, unverified).
