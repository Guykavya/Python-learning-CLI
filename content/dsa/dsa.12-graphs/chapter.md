# dsa.12 Graphs

## 1. Things connected to things

A road map is a set of cities and the roads between them. A social network is a set of people and the friendships between them. A course catalogue is a set of courses and the "you must pass this one first" rules between them. A maze is a set of cells and the open doors between neighbouring cells. These look like four different problems, but they all have the same shape: **things**, and **connections between pairs of things**.

That shape is called a **graph**. The things are **vertices** (or **nodes**), and the connections are **edges**. Once you see a problem as a graph, one small toolbox of algorithms answers a huge number of questions:

- "Can I get from here to there?" (search: BFS or DFS)
- "What is the fewest number of steps?" (BFS)
- "What is the cheapest route?" (Dijkstra, Bellman-Ford, Floyd-Warshall)
- "In what order can I do these tasks?" (topological sort)
- "Which groups are connected?" (connected components, Union-Find)
- "What is the cheapest way to connect everything?" (minimum spanning tree)
- "Which single road, if closed, would cut the city in two?" (bridges)

You already know one kind of graph very well: a **tree** (dsa.10). A tree is a graph that is connected and has no cycles. Everything you learned there (depth-first and breadth-first traversals, recursion that returns an answer from each subtree) carries over. What is new in a general graph is that **a vertex can be reached by more than one route**, and that you can **walk in a circle**. Both facts lead to the most important rule of this module:

> In a graph, always remember which vertices you have already visited. Otherwise you visit them again, and on a cycle you never stop.

### The vocabulary

```text
    A --- B --- E            undirected: the road A-B works both ways
    |     |
    C --- D     F --- G      two separate pieces (components)

    1 ---> 2 ---> 3          directed: you may go 1 -> 2, not 2 -> 1
    ^             |
    +-------------+          a directed cycle 1 -> 2 -> 3 -> 1
```

| Word | Meaning |
|---|---|
| vertex (node) | a thing: a city, a person, a cell, a course |
| edge | a connection between two vertices |
| undirected edge | works both ways (friendship, a two-way road) |
| directed edge (arc) | works one way: `u -> v` (a one-way street, "A must come before B", "follows") |
| weight | a number on an edge: a distance, a cost, a time |
| neighbours of `u` | the vertices joined to `u` by an edge (for directed graphs: the ones `u` points to) |
| degree | the number of edges at a vertex; a directed graph has an **in-degree** and an **out-degree** |
| path | a sequence of vertices, each joined to the next by an edge |
| cycle | a path that comes back to its start without reusing an edge |
| connected | (undirected) every vertex can reach every other |
| component | a largest connected piece of an undirected graph |
| DAG | a **d**irected **a**cyclic **g**raph: directed, with no directed cycle |
| sparse / dense | few edges (about `V`) / many edges (close to `V * V`) |

We write **`V`** for the number of vertices and **`E`** for the number of edges. Every complexity in this module is written in terms of `V` and `E`. A simple undirected graph has at most `V(V - 1) / 2` edges, so `E` can be anything from `0` to about `V² / 2`. That range is why we keep both letters instead of writing one `n`: an algorithm that costs `O(V + E)` is linear on a sparse road map and quadratic on a dense "everyone knows everyone" graph.

### A first look

Here is the top graph of the picture, built from its list of edges. For each vertex we keep the list of its neighbours.

```python
from collections import defaultdict, deque
import heapq

edges = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("B", "E"), ("F", "G")]

graph = defaultdict(list)
for u, v in edges:
    graph[u].append(v)          # undirected: store the edge in BOTH directions
    graph[v].append(u)

for vertex in sorted(graph):
    print(vertex, graph[vertex], "degree", len(graph[vertex]))
print("sum of degrees:", sum(len(n) for n in graph.values()), "edges:", len(edges))
```
```text
A ['B', 'C'] degree 2
B ['A', 'D', 'E'] degree 3
C ['A', 'D'] degree 2
D ['B', 'C'] degree 2
E ['B'] degree 1
F ['G'] degree 1
G ['F'] degree 1
sum of degrees: 12 edges: 6
```

The last line shows the **handshake rule**: in an undirected graph, the degrees add up to exactly `2E`, because every edge is counted once at each end. It is a quick check that you stored both directions.

### What you can do after this module

1. **Store a graph** as an adjacency list, an adjacency matrix or an edge list, and treat a grid or a puzzle as a graph without building it.
2. **Search it** with BFS and DFS, find shortest paths by number of steps, and count connected components.
3. **Order tasks** with a topological sort, and **detect cycles** in directed and undirected graphs.
4. **Check bipartiteness** (can the vertices be split into two sides?).
5. **Merge groups** quickly with Union-Find.
6. **Find shortest weighted paths** with Dijkstra, 0-1 BFS, Bellman-Ford and Floyd-Warshall, and **pick the right one** from the edge weights.
7. **Build a minimum spanning tree** with Kruskal or Prim.
8. **Find strongly connected components, bridges and articulation points** with low-link values.
9. **Model a word problem as a graph**: decide what the vertices are, what the edges are, and which traversal answers the question.

## 2. Storing a graph

Before any algorithm, you must decide how the graph lives in memory. There are three standard ways. They hold the same information but make different questions cheap.

### Edge list

The simplest: a list of pairs (or triples, with a weight).

```text
edges = [(0, 1), (0, 2), (1, 2), (2, 3)]          weighted: [(0, 1, 4), (0, 2, 1), ...]
```

An edge list is how graphs usually arrive in the input ("the next `E` lines each hold `u v w`"). It is perfect when an algorithm looks at **all edges, in any order**: Kruskal's MST (section 15) sorts them, and Bellman-Ford (section 12) loops over them. It is bad at "who are the neighbours of `u`?": you must scan all `E` edges.

### Adjacency list

For each vertex, the list of its neighbours. This is the default representation for almost every algorithm in this module, because a search asks exactly one question again and again: "where can I go from `u`?".

If the vertices are numbered `0 .. n-1`, use a **list of lists**. If they have names, use a **dictionary of lists**. For weights, store pairs `(neighbour, weight)`.

```python
def build_adj(n, edge_list, directed=False):
    adj = [[] for _ in range(n)]        # NOT [[]] * n: that would be n copies of ONE list
    for u, v, *rest in edge_list:
        w = rest[0] if rest else 1
        adj[u].append((v, w))
        if not directed:
            adj[v].append((u, w))
    return adj

adj = build_adj(4, [(0, 1, 4), (0, 2, 1), (1, 2, 2), (2, 3, 5)])
for u, nbrs in enumerate(adj):
    print(u, nbrs)
```
```text
0 [(1, 4), (2, 1)]
1 [(0, 4), (2, 2)]
2 [(0, 1), (1, 2), (3, 5)]
3 [(2, 5)]
```

Memory is `O(V + E)`: one list per vertex, and one entry per edge end. Listing the neighbours of `u` costs `O(degree(u))`, which is as fast as it can be.

### Adjacency matrix

A `V x V` table: `matrix[u][v]` is `1` (or the weight) if there is an edge `u -> v`, and `0` (or "infinity") if not.

```python
def build_matrix(n, edge_list):
    matrix = [[0] * n for _ in range(n)]
    for u, v in edge_list:
        matrix[u][v] = matrix[v][u] = 1
    return matrix

matrix = build_matrix(4, [(0, 1), (0, 2), (1, 2), (2, 3)])
for row in matrix:
    print(row)
print("is 1-3 an edge?", matrix[1][3] == 1, "  is 2-3 an edge?", matrix[2][3] == 1)
```
```text
[0, 1, 1, 0]
[1, 0, 1, 0]
[1, 1, 0, 1]
[0, 0, 1, 0]
is 1-3 an edge? False   is 2-3 an edge? True
```

The matrix answers "is there an edge between `u` and `v`?" in `O(1)`. But it always costs `O(V²)` memory, and listing the neighbours of `u` costs `O(V)` (scan a whole row), even if `u` has one neighbour. For an undirected graph the matrix is symmetric: `matrix[u][v] == matrix[v][u]`.

### Which one?

| Question | Edge list | Adjacency list | Adjacency matrix |
|---|---|---|---|
| memory | `O(E)` | `O(V + E)` | `O(V²)` |
| neighbours of `u` | `O(E)` | `O(degree(u))` | `O(V)` |
| is `u-v` an edge? | `O(E)` | `O(degree(u))` (or `O(1)` with sets) | `O(1)` |
| visit every edge | `O(E)` | `O(V + E)` | `O(V²)` |
| typical use | input format, Kruskal, Bellman-Ford | BFS, DFS, Dijkstra, almost everything | dense graphs, Floyd-Warshall, small `V` |

A graph with `V = 100,000` cities and `E = 300,000` roads is fine as an adjacency list (about 700,000 entries) but impossible as a matrix (10 billion cells). On the other hand, Floyd-Warshall (section 13) fills a full distance table anyway, so a matrix is natural there.

If you need both fast neighbour lists **and** fast "is this an edge?", use a list of **sets**: `adj[u]` is a set, so `v in adj[u]` is `O(1)` on average.

### A grid is a graph you do not build

A maze, an island map or a game board is a graph: each open cell is a vertex, and there is an edge between two cells that touch. You never build an adjacency list for it. Instead you **compute the neighbours on the fly**:

```python
GRID = ["..#.",
        ".##.",
        "...."]

def grid_neighbours(grid, r, c):
    rows, cols = len(grid), len(grid[0])
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):      # up, down, left, right
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
            yield nr, nc

print(list(grid_neighbours(GRID, 0, 0)))
print(list(grid_neighbours(GRID, 2, 1)))
print(list(grid_neighbours(GRID, 0, 3)))
```
```text
[(1, 0), (0, 1)]
[(2, 0), (2, 2)]
[(1, 3)]
```

A grid with `R` rows and `C` columns has `V = R * C` vertices and at most `4V` edge ends, so `E = O(V)`: grids are always sparse. For eight directions (diagonals too), add the four pairs `(±1, ±1)`.

### Implicit graphs: states and moves

Sometimes the vertices are not places at all, but **states** of a puzzle, and the edges are **moves**. A combination lock with four wheels shows a state like `"0000"`; one move turns one wheel up or down by one. "What is the fewest number of moves to reach `"0202"`?" is a shortest-path question in a graph with 10,000 vertices that you never write down. You only need a function that lists the neighbours of a state:

```python
def lock_neighbours(state):
    for i in range(4):
        digit = int(state[i])
        for d in (-1, 1):
            new = (digit + d) % 10
            yield state[:i] + str(new) + state[i + 1:]

print(list(lock_neighbours("0000")))
```
```text
['9000', '1000', '0900', '0100', '0090', '0010', '0009', '0001']
```

Every algorithm in this module only ever asks "what are the neighbours of `u`?". So it works the same on a list of lists, a dictionary, a grid or a puzzle, as long as you can answer that question.

### Traps when building a graph

1. **Undirected edges stored once.** If the input says "`u v` are friends", add `v` to `u`'s list **and** `u` to `v`'s list. Forgetting one direction gives searches that "cannot reach" vertices they should.
2. **Vertices with no edges disappear.** If you build a dictionary only from the edge list, an isolated vertex is never a key. With numbered vertices, create `adj = [[] for _ in range(n)]` for **all** `n` first.
3. **`[[]] * n`.** This makes `n` references to one single list; every vertex then shares the same neighbours. Use a comprehension.
4. **1-based input.** Many inputs number vertices `1 .. n`. Either subtract one when reading, or make `n + 1` lists and ignore index `0`. Decide once and stay consistent.
5. **Self-loops and parallel edges.** An edge `u -> u`, or two edges between the same pair, are allowed in many inputs. Most algorithms cope, but cycle detection and bridges (sections 6 and 17) need care.

**Try it 1.** Build the adjacency list (list of lists, vertices `1 .. 5`, 1-based input) of the undirected graph with edges `1-2, 2-3, 3-1, 4-5`, and print the degree of every vertex. Which vertex has degree 0 if you add a sixth vertex?

<details><summary>Answer</summary>

```python
n = 6
input_edges = [(1, 2), (2, 3), (3, 1), (4, 5)]
adj1 = [[] for _ in range(n + 1)]          # index 0 is unused
for u, v in input_edges:
    adj1[u].append(v)
    adj1[v].append(u)
print([len(adj1[v]) for v in range(1, n + 1)])
```
```text
[2, 2, 2, 1, 1, 0]
```

Vertex 6 has degree 0. It exists only because we created `n + 1` lists up front; a dictionary built from the edges alone would not know about it.

</details>

## 3. Breadth-first search

### The idea: waves

Drop a stone in a pond. The ripple reaches everything one metre away, then everything two metres away, and so on. **Breadth-first search** (BFS) explores a graph the same way: first the start, then all its neighbours (distance 1), then all their new neighbours (distance 2), wave after wave.

You met BFS on trees as **level order** in dsa.10 (section 6): a queue, `popleft` the front, append the children. In a graph we need one more thing: a **visited** record, because a vertex can be reached from several neighbours and we must handle it only once.

```python
def bfs(graph, start):
    dist = {start: 0}               # doubles as the "visited" record
    parent = {start: None}
    queue = deque([start])
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            if v not in dist:       # first time we see v
                dist[v] = dist[u] + 1
                parent[v] = u
                queue.append(v)
    return order, dist, parent

order, dist, parent = bfs(graph, "A")
print("order :", order)
print("dist  :", dist)
print("parent:", parent)
```
```text
order : ['A', 'B', 'C', 'D', 'E']
dist  : {'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2}
parent: {'A': None, 'B': 'A', 'C': 'A', 'D': 'B', 'E': 'B'}
```

### Tracing it by hand

The graph from section 1, with the neighbour lists in the order we stored them (`A: [B, C]`, `B: [A, D, E]`, `C: [A, D]`, `D: [B, C]`, `E: [B]`):

```text
    A --- B --- E
    |     |
    C --- D
```

| Step | Pop | Look at neighbours | New ones (dist) | Queue after |
|---|---|---|---|---|
| start | | | A (0) | `[A]` |
| 1 | A | B, C | B (1), C (1) | `[B, C]` |
| 2 | B | A seen, D, E | D (2), E (2) | `[C, D, E]` |
| 3 | C | A seen, D seen | none | `[D, E]` |
| 4 | D | B seen, C seen | none | `[E]` |
| 5 | E | B seen | none | `[]` |

`F` and `G` are never reached: they are in another component. `dist` has no key for them, which is how you answer "can I reach F from A?" (no).

### Why BFS gives the shortest path (in steps)

The queue always holds vertices of at most two neighbouring distances, `d` then `d + 1`, in that order: we pop distance-`d` vertices and push their new neighbours with distance `d + 1` at the back. So vertices leave the queue in order of distance. When `v` is seen for the first time, it is seen from a vertex `u` with the smallest possible distance, so `dist[u] + 1` is the smallest possible distance of `v`. No later route can be shorter, because every later `u` is at least as far away.

This is true only when **every edge counts as one step**. With weights (a 1 km road and a 50 km road), "fewest edges" is not "shortest distance"; that needs Dijkstra (section 10).

### Getting the path back

`dist` gives the length; `parent` gives the path. Walk from the target back to the start through `parent`, then reverse.

```python
def path_to(parent, target):
    if target not in parent:
        return None                 # not reachable
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    return path[::-1]

print(path_to(parent, "D"))
print(path_to(parent, "E"))
print(path_to(parent, "F"))
```
```text
['A', 'B', 'D']
['A', 'B', 'E']
None
```

The `parent` links form a tree, the **BFS tree**: every reached vertex points to the vertex that discovered it. There may be several shortest paths (`A B D` and `A C D` both have two edges); BFS returns the one its neighbour order found first.

### Complexity

Every reachable vertex enters the queue **once** (we mark it when we push it), and when it leaves the queue we look at each of its edges once. So BFS costs **`O(V + E)`** time with an adjacency list, and `O(V)` extra memory for the queue and `dist`. With an adjacency matrix, listing neighbours costs `O(V)` per vertex, so BFS costs `O(V²)`.

### Trap: mark when you push, not when you pop

A very common bug is to check "visited" only when a vertex is **popped**:

```python
def bfs_mark_on_pop(graph, start):
    seen, queue, pushes = set(), deque([start]), 1
    while queue:
        u = queue.popleft()
        if u in seen:
            continue
        seen.add(u)
        for v in graph[u]:
            if v not in seen:
                queue.append(v)
                pushes += 1
    return pushes

def bfs_mark_on_push(graph, start):
    seen, queue, pushes = {start}, deque([start]), 1
    while queue:
        u = queue.popleft()
        for v in graph[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
                pushes += 1
    return pushes

# a complete graph: every vertex joined to every other
n = 200
complete = {u: [v for v in range(n) if v != u] for u in range(n)}
print("mark on pop :", bfs_mark_on_pop(complete, 0), "pushes")
print("mark on push:", bfs_mark_on_push(complete, 0), "pushes")
```
```text
mark on pop : 19901 pushes
mark on push: 200 pushes
```

Both versions visit the same vertices, and the "mark on pop" one even gives correct distances if you store them at pop time. But it lets the same vertex sit in the queue many times: on this dense graph, about one push per edge instead of one per vertex. On a big grid it is the difference between passing and "time limit exceeded" or running out of memory. **Mark a vertex as visited the moment you put it in the queue.**

### BFS on a grid: the shortest way through a maze

The same code, with `grid_neighbours` instead of a neighbour list, and `(row, col)` pairs as vertices.

```python
def maze_shortest(grid, start, goal):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        if (r, c) == goal:
            return dist[(r, c)]
        for cell in grid_neighbours(grid, r, c):
            if cell not in dist:
                dist[cell] = dist[(r, c)] + 1
                queue.append(cell)
    return -1                                        # the goal cannot be reached

MAZE = ["S.#....",
        ".##.##.",
        "...#...",
        ".#...#G"]
print(maze_shortest(MAZE, (0, 0), (3, 6)))
print(maze_shortest(["S#G"], (0, 0), (0, 2)))
```
```text
11
-1
```

We can stop as soon as the goal leaves the queue (or even as soon as it is first pushed): BFS reaches it with its final distance. `-1` means "unreachable": the wall in `"S#G"` blocks the only route.

### Multi-source BFS

"For every empty cell, how far is the nearest exit?" You could run one BFS from every cell: `O(V)` searches of `O(V)` each, `O(V²)`. Much better: **put all the exits in the queue at the start**, each with distance 0, and run one BFS. The waves start from all exits at once, and each cell is first reached by the wave of the nearest exit. Cost: `O(V + E)`, a single search.

```python
def distance_to_nearest(grid, sources):
    rows, cols = len(grid), len(grid[0])
    dist = [[-1] * cols for _ in range(rows)]
    queue = deque()
    for r, c in sources:
        dist[r][c] = 0
        queue.append((r, c))
    while queue:
        r, c = queue.popleft()
        for nr, nc in grid_neighbours(grid, r, c):
            if dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                queue.append((nr, nc))
    return dist

ROOM = ["E...",
        ".##.",
        "...E"]
for row in distance_to_nearest(ROOM, [(0, 0), (2, 3)]):
    print(" ".join(f"{d:2}" for d in row))
```
```text
 0  1  2  2
 1 -1 -1  1
 2  2  1  0
```

Walls stay at `-1`. Each open cell holds the distance to the closer of the two exits `E`. The same trick solves "rotting oranges" (all rotten oranges start the queue; the answer is the largest distance) and "walls and gates".

### BFS on a state graph

Back to the lock. Some states are **dead ends** (the lock jams); find the fewest moves from `"0000"` to the target, or `-1`.

```python
def open_lock(deadends, target):
    dead = set(deadends)
    if "0000" in dead:
        return -1
    dist = {"0000": 0}
    queue = deque(["0000"])
    while queue:
        state = queue.popleft()
        if state == target:
            return dist[state]
        for nxt in lock_neighbours(state):
            if nxt not in dist and nxt not in dead:
                dist[nxt] = dist[state] + 1
                queue.append(nxt)
    return -1

print(open_lock(["0201", "0101", "0102", "1212", "2002"], "0202"))
print(open_lock(["8888"], "0009"))
print(open_lock(["8887", "8889", "8878", "8898", "8788", "8988", "7888", "9888"], "8888"))
```
```text
6
1
-1
```

`"0009"` takes one move (turn the last wheel down from 0 to 9). In the third case every neighbour of `"8888"` is dead, so it can never be reached. The graph has 10,000 vertices and each has 8 neighbours, so one BFS is at most about 90,000 steps.

**Predict the output.** In the graph `graph` of section 1, what are `dist["E"]` and `path_to(parent, "D")` if the edge `("A", "C")` is removed?

<details><summary>Answer</summary>

`dist["E"]` stays `2` (`A B E`). `D` is still reached in two steps, `A B D`: with `A-C` gone, `C` is reached only through `D`, so `C` is now at distance 3.

```python
g2 = defaultdict(list)
for u, v in edges:
    if (u, v) != ("A", "C"):
        g2[u].append(v)
        g2[v].append(u)
_, d2, p2 = bfs(g2, "A")
print(d2["E"], path_to(p2, "D"), d2["C"])
```
```text
2 ['A', 'B', 'D'] 3
```

</details>

## 4. Depth-first search

### The idea: go deep, then back up

**Depth-first search** (DFS) explores like a person in a maze holding a ball of string: walk forward as long as there is an unvisited way on; when you reach a dead end, walk back to the last junction with an untried way, and try it. This is the preorder traversal of dsa.10 (section 4), plus a visited set.

The recursive version is the shortest to write:

```python
def dfs_recursive(graph, start):
    visited, order = set(), []

    def visit(u):
        visited.add(u)
        order.append(u)
        for v in graph[u]:
            if v not in visited:
                visit(v)

    visit(start)
    return order

print(dfs_recursive(graph, "A"))
```
```text
['A', 'B', 'D', 'C', 'E']
```

Trace: `A` goes to its first neighbour `B`; `B`'s first unvisited neighbour is `D`; `D`'s neighbours are `B` (visited) and `C`, so we go to `C`; `C`'s neighbours `A` and `D` are visited, so we back up to `D`, then to `B`, whose next neighbour is `E`. Compare with BFS, which visited `A B C D E`: DFS dives to `C` through `D` before it ever tries `E`.

### The recursion-limit trap

Python allows only about 1,000 nested calls (dsa.01). A recursive DFS goes as deep as the longest path it walks, and in a graph that can be **every vertex**. A simple chain of 5,000 vertices is enough to crash it:

```python
import sys

chain = {i: [i + 1] for i in range(4999)}
chain[4999] = []
print("recursion limit:", sys.getrecursionlimit())
try:
    print(len(dfs_recursive(chain, 0)))
except RecursionError:
    print("RecursionError on a chain of 5000 vertices")
```
```text
recursion limit: 1000
RecursionError on a chain of 5000 vertices
```

Inputs in contests and real data easily have 100,000 vertices in one long chain, or a 1000 x 1000 grid where a DFS snake visits every cell. You have three options:

1. **Write DFS with an explicit stack** (below). This is the safe default.
2. Raise the limit with `sys.setrecursionlimit(10**6)`. This removes the Python check, but each call still uses memory on the real machine stack. On deep inputs the interpreter can then crash with no error message at all ("segmentation fault"). Use it only when you know the depth is moderate.
3. Use BFS when the order does not matter (counting components, "is it reachable?").

### DFS with a stack

Replace the call stack with a list used as a stack (dsa.08):

```python
def dfs_iterative(graph, start):
    visited, order = set(), []
    stack = [start]
    while stack:
        u = stack.pop()
        if u in visited:
            continue                 # pushed more than once; handle it only the first time
        visited.add(u)
        order.append(u)
        for v in reversed(graph[u]): # reversed, so the first neighbour is popped first
            if v not in visited:
                stack.append(v)
    return order

print(dfs_iterative(graph, "A"))
print(len(dfs_iterative(chain, 0)))
```
```text
['A', 'B', 'D', 'C', 'E']
5000
```

Two details make this the same order as the recursive version:

- **Mark on pop, not on push.** This is the opposite of BFS! A vertex may be pushed several times (by several neighbours), and the **last** push is the one that is popped first, which is exactly the vertex recursion would enter next. If you marked on push, you would lock in the earliest discovery and get a different order (still a valid search, but not a depth-first order). The `if u in visited: continue` skips the extra copies. The stack can hold up to `O(E)` entries.
- **Push neighbours in reverse**, so that the first neighbour ends on top.

When you only need "which vertices are reachable?", any order is fine, and you can mark on push like BFS.

### A DFS that knows when it leaves a vertex

Some algorithms (topological sort, cycle detection in directed graphs, strongly connected components) need to know when DFS has **finished** a vertex, that is, when all of its descendants are done. In the recursive version that is the line after the loop. With a stack, keep for each vertex an **iterator** over its neighbours, so you can come back and continue where you left off:

```python
def dfs_enter_exit(graph, start):
    """Return the events ("e", u) for enter and ("x", u) for exit, in depth-first order."""
    events = [("e", start)]
    visited = {start}
    stack = [(start, iter(graph[start]))]
    while stack:
        u, neighbours = stack[-1]
        v = next(neighbours, None)
        if v is None:                       # no neighbour left: u is finished
            stack.pop()
            events.append(("x", u))
        elif v not in visited:
            visited.add(v)
            events.append(("e", v))
            stack.append((v, iter(graph[v])))
    return events

print(" ".join(kind + u for kind, u in dfs_enter_exit(graph, "A")))
```
```text
eA eB eD eC xC xD eE xE xB xA
```

Read `eA` as "enter A" and `xA` as "exit A". The events nest like brackets: `eA eB eD eC xC xD eE xE xB xA`. A vertex is entered before every vertex below it and exited after all of them. This bracket structure is the key to sections 6, 7, 16 and 17. (`next(it, None)` returns `None` when the iterator is used up; this works as long as `None` is never a vertex.)

Many people number the events with a clock: **`tin[u]`**, the time `u` was entered, and **`tout[u]`**, the time it was exited. Then `v` is a descendant of `u` in the DFS tree exactly when `tin[u] < tin[v]` and `tout[v] < tout[u]`.

### Complexity and what DFS is good for

Like BFS: each vertex is entered once and each edge is looked at once (twice if undirected), so DFS costs **`O(V + E)`** time and `O(V)` memory (`O(E)` for the "mark on pop" stack).

| | BFS (queue) | DFS (stack or recursion) |
|---|---|---|
| order | wave by wave, by distance | as deep as possible, then back up |
| shortest path in steps | **yes** | no |
| finish time of a vertex | no | **yes** (topological order, SCC, bridges) |
| memory | the widest wave | the longest path |
| typical uses | fewest moves, nearest X, levels | reachability, components, cycles, ordering, backtracking |

For "is it reachable?" and "how many components?", both work. For "fewest steps", only BFS. For anything that needs "after all of `u`'s descendants", DFS.

**Try it 2.** A DFS can find a path, but not always the shortest. On the graph below, what path does `dfs_recursive`-style search find from `0` to `3`, and what does BFS find?

```text
0 --- 1 --- 2 --- 3          adjacency in this order:
|                 |          0: [1, 3]  1: [0, 2]  2: [1, 3]  3: [2, 0]
+-----------------+
```

<details><summary>Answer</summary>

```python
ring = {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [2, 0]}

def dfs_path(graph, start, goal, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    if start == goal:
        return [start]
    for v in graph[start]:
        if v not in visited:
            rest = dfs_path(graph, v, goal, visited)
            if rest:
                return [start] + rest
    return None

_, _, ring_parent = bfs(ring, 0)
print("DFS:", dfs_path(ring, 0, 3))
print("BFS:", path_to(ring_parent, 3))
```
```text
DFS: [0, 1, 2, 3]
BFS: [0, 3]
```

DFS follows the first neighbour `1` and keeps going, so it finds the long way round with 3 edges. BFS finds the direct edge.

</details>

## 5. Connected components

### Counting the pieces

An undirected graph falls apart into **connected components**: largest groups in which everyone can reach everyone. One search from a vertex `s` visits exactly the component of `s`. So to find all components, **start a new search from every vertex that is not yet visited**, and count the searches.

```python
def components(graph, vertices):
    """Return (number of components, {vertex: component number})."""
    comp = {}
    count = 0
    for s in vertices:
        if s in comp:
            continue                    # already found from an earlier start
        comp[s] = count
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if v not in comp:
                    comp[v] = count
                    queue.append(v)
        count += 1
    return count, comp

count, comp = components(graph, "ABCDEFGH")      # H has no edges at all
print(count)
print(comp)
```
```text
3
{'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 1, 'G': 1, 'H': 2}
```

Three components: `{A, B, C, D, E}`, `{F, G}` and the lonely `{H}`. Notice that we passed the **list of all vertices** separately: `H` has no edges, so it appears in no edge and would be missed if we only looped over the keys built from the edges.

The outer loop visits every vertex once, and all the searches together look at every edge once per end, so the whole thing is still **`O(V + E)`**, not `O(V)` searches times `O(V + E)`.

The `comp` dictionary is now a fast answer to "are `x` and `y` connected?": compare `comp[x]` and `comp[y]` in `O(1)`. (If edges keep arriving, the labels go stale; Union-Find in section 9 handles that case.)

### Islands on a grid

"Count the islands": `"1"` is land, `"0"` is water, and land cells that touch up/down/left/right form one island. Each island is a component of the grid graph. This time we use DFS with a stack, and we also measure the size of each island.

```python
def islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    sizes = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != "1" or seen[r][c]:
                continue
            seen[r][c] = True
            stack, size = [(r, c)], 0
            while stack:
                cr, cc = stack.pop()
                size += 1
                for nr, nc in ((cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1" and not seen[nr][nc]:
                        seen[nr][nc] = True          # reachability only: mark on push is fine
                        stack.append((nr, nc))
            sizes.append(size)
    return sizes

SEA = ["11000",
       "11010",
       "00011",
       "10000"]
sizes = islands(SEA)
print(len(sizes), "islands, sizes", sizes, "largest", max(sizes))
```
```text
3 islands, sizes [4, 3, 1] largest 4
```

A popular shortcut is to "sink" each land cell (set it to `"0"`) instead of keeping `seen`. It saves memory, but it destroys the input; copy the grid first if the caller still needs it.

**Try it 3.** `friends[i][j] == 1` means people `i` and `j` are direct friends (an adjacency matrix). A *friend circle* is a component. Count the circles for the matrix below.

```text
friends = [[1, 1, 0, 0],
           [1, 1, 0, 0],
           [0, 0, 1, 1],
           [0, 0, 1, 1]]           and the same with person 3 friends with nobody
```

<details><summary>Answer</summary>

```python
def friend_circles(friends):
    n = len(friends)
    seen = [False] * n
    circles = 0
    for s in range(n):
        if seen[s]:
            continue
        circles += 1
        seen[s] = True
        stack = [s]
        while stack:
            u = stack.pop()
            for v in range(n):                       # a matrix: scan the whole row, O(V)
                if friends[u][v] and not seen[v]:
                    seen[v] = True
                    stack.append(v)
    return circles

m1 = [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]]
m2 = [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
print(friend_circles(m1), friend_circles(m2))
```
```text
2 3
```

With a matrix each vertex scans a full row, so this costs `O(V²)`, which is the size of the input anyway.

</details>

## 6. Cycle detection

"Is there a cycle?" sounds like one question, but it has **two different answers** for undirected and for directed graphs. Using the wrong one is one of the most common graph bugs.

### Undirected graphs: a seen vertex that is not my parent

In an undirected graph, every edge looks like a tiny cycle: `u -> v -> u`. That is not a real cycle; it is the same edge walked back. So during the search, when we look from `u` at a neighbour `v` that is already visited, there are two cases:

- `v` is the vertex we came from (the **parent** of `u`): just the same edge backwards. Ignore it.
- any other visited `v`: there is a second route to `v`, so there is a **cycle**.

```python
def has_cycle_undirected(n, edge_list):
    adj = [[] for _ in range(n)]
    for u, v in edge_list:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, -1)]                      # (vertex, the vertex we came from)
        while stack:
            u, par = stack.pop()
            for v in adj[u]:
                if v == par:
                    continue                   # the edge we arrived by
                if seen[v]:
                    return True                # a second way to reach v
                seen[v] = True
                stack.append((v, u))
    return False

print(has_cycle_undirected(4, [(0, 1), (1, 2), (2, 3)]))            # a path
print(has_cycle_undirected(4, [(0, 1), (1, 2), (2, 0), (2, 3)]))    # triangle 0-1-2
print(has_cycle_undirected(5, [(0, 1), (3, 4), (4, 2), (2, 3)]))    # cycle in the 2nd component
```
```text
False
True
True
```

Why is this right even though the stack does not visit in a "true DFS" order? We mark a vertex when we first discover it, through one edge, the **tree edge**. Every other edge between two vertices of the same component is examined at a moment when both ends are already marked (if the other end were not marked, this edge would have become its tree edge). A component with `k` vertices and no cycle is a tree with exactly `k - 1` edges, all of them tree edges; any extra edge closes a cycle. Cost: `O(V + E)`.

That last fact gives a one-line check for a whole graph: **a forest (no cycles) has exactly `V - C` edges**, where `C` is the number of components. So an undirected graph has a cycle exactly when `E > V - C`. A connected graph is a tree exactly when `E == V - 1`.

**Parallel edges and self-loops.** If the input may contain the same edge twice (`0-1` and `0-1` again), that is a cycle of length two. Does "skip the parent" skip both copies and miss it? Only on one side. Vertex `1` skips both copies back to its parent `0`, but vertex `0`, which discovered `1` through the first copy, meets the second copy while `1` is already marked, and reports the cycle. A self-loop `0-0` is caught too, because `0` is never its own parent.

```python
print("double edge 0-1:", has_cycle_undirected(2, [(0, 1), (0, 1)]))
print("self-loop 0-0  :", has_cycle_undirected(1, [(0, 0)]))
```
```text
double edge 0-1: True
self-loop 0-0  : True
```

So for cycle detection the parent check is safe. For **bridges** (section 17) it is not: there, skipping every edge to the parent makes a doubled edge look like a bridge, and we must skip only the one edge we arrived by, identified by its index.

### Directed graphs: three colours

In a directed graph, `u -> v` and `v -> u` are two different edges, and together they **are** a real cycle. And a vertex reached twice is **not** a sign of a cycle. Look at this "diamond":

```text
      A
     / \           A -> B, A -> C, B -> D, C -> D
    v   v
    B   C          D is reached twice (through B and through C),
     \ /           but there is no way to go round in a circle.
      v
      D
```

A directed cycle means: during DFS, we find an edge to a vertex that is **still on the current path** (we entered it but have not exited it). We track three states, traditionally called colours:

- **white**: not visited yet,
- **grey**: entered, not exited: on the current DFS path (on the recursion stack),
- **black**: exited: it and everything reachable from it is finished, and contains no cycle back to the current path.

An edge to a **grey** vertex is a **back edge**: it closes a cycle. An edge to a **black** vertex is harmless (like `C -> D` in the diamond, when `D` was finished through `B`).

```python
WHITE, GREY, BLACK = 0, 1, 2

def has_cycle_directed(graph):
    color = {u: WHITE for u in graph}

    def visit(u):
        color[u] = GREY
        for v in graph[u]:
            if color[v] == GREY:
                return True                    # back edge: v is on the current path
            if color[v] == WHITE and visit(v):
                return True
        color[u] = BLACK                       # finished, no cycle through u
        return False

    return any(color[u] == WHITE and visit(u) for u in graph)

def has_cycle_wrong(graph):
    """The undirected idea used on a directed graph: 'seen before' = cycle."""
    visited = set()
    def visit(u):
        visited.add(u)
        for v in graph[u]:
            if v in visited or visit(v):
                return True
        return False
    return any(u not in visited and visit(u) for u in graph)

diamond = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
loop = {"A": ["B"], "B": ["C"], "C": ["A"]}
print("diamond: three colours", has_cycle_directed(diamond), "| 'seen' check", has_cycle_wrong(diamond))
print("loop   : three colours", has_cycle_directed(loop), "| 'seen' check", has_cycle_wrong(loop))
```
```text
diamond: three colours False | 'seen' check True
loop   : three colours True | 'seen' check True
```

The "seen" check calls the diamond cyclic, which is wrong. And the other way round fails too: an **undirected** graph stored in both directions has `u -> v -> u` for every edge, so the three-colour method calls every undirected graph with an edge cyclic:

```python
two_way = {"A": ["B"], "B": ["A"]}
print("undirected edge A-B, three colours:", has_cycle_directed(two_way))
```
```text
undirected edge A-B, three colours: True
```

| Graph | Cycle means | Method |
|---|---|---|
| undirected | a visited neighbour that is not the edge we came by | parent / edge-id check, Union-Find, or `E > V - C` |
| directed | an edge to a vertex **on the current path** | three colours (grey = on the path), or Kahn's algorithm (section 7) |

### Finding the cycle, without recursion

The recursive version above can hit the recursion limit (section 4). Here is the iterative version with the iterator stack. It also returns the cycle itself: remember each vertex's parent, and when an edge `u -> v` hits a grey `v`, walk back from `u` to `v`.

```python
def find_cycle_directed(graph):
    color = {u: WHITE for u in graph}
    parent = {}
    for s in graph:
        if color[s] != WHITE:
            continue
        color[s] = GREY
        stack = [(s, iter(graph[s]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                color[u] = BLACK
                stack.pop()
            elif color[v] == GREY:
                cycle = [u]
                while cycle[-1] != v:
                    cycle.append(parent[cycle[-1]])
                return cycle[::-1]             # v ... u, and the edge u -> v closes it
            elif color[v] == WHITE:
                color[v] = GREY
                parent[v] = u
                stack.append((v, iter(graph[v])))
    return None

g = {1: [2], 2: [3, 5], 3: [4], 4: [2], 5: []}
print(find_cycle_directed(g))
print(find_cycle_directed(diamond))
print(find_cycle_directed({7: [7]}))
```
```text
[2, 3, 4]
None
[7]
```

`2 -> 3 -> 4 -> 2` is the cycle; `1` leads into it but is not part of it. A self-loop `7 -> 7` is a cycle of one vertex.

## 7. Topological sort

### Ordering with "must come before"

You must take some courses before others. You must put on socks before shoes. A build system must compile a library before the program that uses it. Each rule "`u` before `v`" is a directed edge `u -> v`. A **topological order** is a list of all vertices in which every edge points **forward**: `u` comes before `v` for every edge `u -> v`.

```text
   intro ----> dsa ----> algorithms ----+
                ^                       |
   math --------+                       v
     |                                  ml
     +-------> stats -------------------^

   intro ----> web
```

A topological order exists **exactly when the graph has no directed cycle** (it is a DAG). If `a -> b -> c -> a`, then `a` must come before itself, which is impossible. There are usually many valid orders.

### Kahn's algorithm: repeatedly take a task with no remaining prerequisites

The **in-degree** of a vertex is the number of edges coming into it: the number of prerequisites it is still waiting for. A vertex with in-degree 0 can go first. Take it, "delete" its outgoing edges (lower the in-degree of each neighbour by 1), and any neighbour that reaches 0 becomes ready. A queue holds the ready vertices.

```python
def kahn(vertices, edge_list):
    adj = {v: [] for v in vertices}
    indeg = {v: 0 for v in vertices}
    for u, v in edge_list:
        adj[u].append(v)
        indeg[v] += 1
    ready = deque(v for v in vertices if indeg[v] == 0)
    order = []
    while ready:
        u = ready.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    if len(order) < len(vertices):
        return None                     # some vertices never became ready: a cycle
    return order

courses = ["intro", "math", "dsa", "stats", "algorithms", "ml", "web"]
rules = [("intro", "dsa"), ("math", "dsa"), ("dsa", "algorithms"), ("math", "stats"),
         ("stats", "ml"), ("algorithms", "ml"), ("intro", "web")]
print(kahn(courses, rules))
print(kahn(courses, rules + [("ml", "intro")]))
```
```text
['intro', 'math', 'web', 'dsa', 'stats', 'algorithms', 'ml']
None
```

Trace the first call. At the start only `intro` and `math` have in-degree 0. Taking `intro` lowers `dsa` to 1 and `web` to 0 (`web` is ready). Taking `math` lowers `dsa` to 0 and `stats` to 0. And so on: each vertex enters the queue the moment its last prerequisite is done.

**Cycle detection for free.** In the second call the rule `ml -> intro` closes the cycle `intro -> dsa -> algorithms -> ml -> intro`. The vertices on a cycle wait for each other forever, their in-degree never reaches 0, and the order comes out short. So Kahn's algorithm is also a cycle detector for directed graphs, and it needs no recursion at all.

Cost: building the in-degrees is `O(V + E)`, and every vertex and edge is handled once more in the loop: **`O(V + E)`**.

### The DFS way: reverse the finishing order

DFS finishes a vertex only after everything reachable from it is finished. So if there is an edge `u -> v` in a DAG, `v` finishes **before** `u` (it is either finished already, or it will be explored and finished inside `u`'s visit; it cannot be grey, because that would be a cycle). Therefore: **list the vertices in the order they finish, then reverse the list.**

```python
def topo_dfs(graph):
    color = {u: WHITE for u in graph}
    finished = []
    for s in graph:
        if color[s] != WHITE:
            continue
        color[s] = GREY
        stack = [(s, iter(graph[s]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                color[u] = BLACK
                finished.append(u)             # u is finished: all it points to is done
                stack.pop()
            elif color[v] == GREY:
                return None                    # a cycle: no order exists
            elif color[v] == WHITE:
                color[v] = GREY
                stack.append((v, iter(graph[v])))
    return finished[::-1]

course_graph = {c: [] for c in courses}
for u, v in rules:
    course_graph[u].append(v)

def is_topological(order, edge_list):
    position = {v: i for i, v in enumerate(order)}
    return all(position[u] < position[v] for u, v in edge_list)

order_dfs = topo_dfs(course_graph)
print(order_dfs, is_topological(order_dfs, rules))
print(is_topological(kahn(courses, rules), rules))
```
```text
['math', 'stats', 'intro', 'web', 'dsa', 'algorithms', 'ml'] True
True
```

The two methods give **different** orders, and both are correct. If a problem says "return any valid order", either will do; tests must then check the order with something like `is_topological`, not compare it with one fixed answer.

| | Kahn (in-degrees + queue) | DFS (reverse finishing order) |
|---|---|---|
| time | `O(V + E)` | `O(V + E)` |
| cycle detection | order shorter than `V` | an edge to a grey vertex |
| recursion | none | none if written with a stack |
| bonus | easy to control the order (use a heap), easy to group into "rounds" | the finishing order is reused for SCCs (section 16) |

### The smallest order, and rounds

If several vertices are ready at the same time, Kahn's algorithm may pick any of them. To get the **lexicographically smallest** order, keep the ready vertices in a **min-heap** (dsa.11) instead of a queue. Cost: `O(V log V + E)`.

To count the **minimum number of semesters** (if you may take any number of ready courses at once), process the ready queue in **rounds**, exactly like level-order BFS: all the vertices ready now form one round.

```python
def smallest_order(n, edge_list):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edge_list:
        adj[u].append(v)
        indeg[v] += 1
    ready = [v for v in range(n) if indeg[v] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        u = heapq.heappop(ready)
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(ready, v)
    return order if len(order) == n else None

def semesters(n, edge_list):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edge_list:
        adj[u].append(v)
        indeg[v] += 1
    ready = deque(v for v in range(n) if indeg[v] == 0)
    rounds, done = 0, 0
    while ready:
        rounds += 1
        for _ in range(len(ready)):            # exactly the vertices of this round
            u = ready.popleft()
            done += 1
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    ready.append(v)
    return rounds if done == n else -1

dag = [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]
print(smallest_order(6, dag))
print(semesters(6, dag))
```
```text
[4, 5, 0, 2, 3, 1]
4
```

### Dynamic programming on a DAG

A topological order is exactly the order in which a DP over a DAG can fill its table: when we reach `v`, every `u` with an edge `u -> v` is already done. **Longest path** is hard in a general graph, but easy in a DAG.

Example: tasks take some days, some tasks must wait for others, and any number of tasks can run in parallel. When is the whole project finished? Each task finishes at `its own duration + the latest finish among its prerequisites`. The answer is the largest finish time: the length of the longest (the **critical**) path.

```python
def project_time(durations, edge_list):
    n = len(durations)
    order = smallest_order(n, edge_list)
    preds = [[] for _ in range(n)]
    for u, v in edge_list:
        preds[v].append(u)
    finish = [0] * n
    for v in order:                            # every predecessor of v is already done
        start = max((finish[u] for u in preds[v]), default=0)
        finish[v] = start + durations[v]
    return finish, max(finish)

durations = [3, 2, 4, 1, 5, 2]
print(project_time(durations, dag))
```
```text
([8, 9, 6, 7, 5, 2], 9)
```

Check task `1`: it waits for `4` (finishes at 5) and `3`. Task `3` waits for `2`, which waits for `5` (finishes at 2), so `2` finishes at `2 + 4 = 6` and `3` at `6 + 1 = 7`. Task `1` starts at `max(5, 7) = 7` and finishes at `9`. The critical path is `5 -> 2 -> 3 -> 1`. Cost: `O(V + E)`.

**Try it 4.** Count the number of different paths from vertex `0` to vertex `4` in the DAG `0->1, 0->2, 1->3, 2->3, 1->4, 3->4`. Use DP in topological order: `ways[v]` = sum of `ways[u]` over the edges `u -> v`.

<details><summary>Answer</summary>

```python
def count_paths(n, edge_list, source, target):
    ways = [0] * n
    ways[source] = 1
    adj = [[] for _ in range(n)]
    for u, v in edge_list:
        adj[u].append(v)
    for u in smallest_order(n, edge_list):
        for v in adj[u]:
            ways[v] += ways[u]                 # every path to u extends to v
    return ways[target]

print(count_paths(5, [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (3, 4)], 0, 4))
```
```text
3
```

The paths are `0 1 4`, `0 1 3 4` and `0 2 3 4`. In a graph with a cycle the number of paths could be infinite, which is why this works only on a DAG.

</details>

## 8. Bipartite graphs

### Two teams

A graph is **bipartite** if its vertices can be split into two sides so that **every edge goes between the sides**, never inside one side. Examples: students and the courses they take; "these two people dislike each other, can we split everybody into two rooms so that no two enemies share a room?"; colouring a map with two colours so that neighbours differ.

```text
    0 ---- 1           square: colour 0 and 2 red, 1 and 3 blue  -> bipartite
    |      |
    3 ---- 2

      0                triangle: 0 red, 1 blue, then 2 must differ from both
     / \               -> impossible: not bipartite
    1 - 2
```

The rule: **a graph is bipartite exactly when it has no cycle of odd length.** Walking around a cycle, the colours alternate red, blue, red, blue; you can only come back to the start's colour after an even number of steps.

### Two-colouring with BFS

Colour the start `0`. Every neighbour of a vertex with colour `c` must get colour `1 - c`. If we ever meet an edge whose two ends have the **same** colour, the graph is not bipartite. Do this from every uncoloured vertex, because each component must be checked.

```python
def two_colour(n, edge_list):
    adj = [[] for _ in range(n)]
    for u, v in edge_list:
        adj[u].append(v)
        adj[v].append(u)
    colour = [-1] * n
    for s in range(n):
        if colour[s] != -1:
            continue
        colour[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if colour[v] == -1:
                    colour[v] = 1 - colour[u]
                    queue.append(v)
                elif colour[v] == colour[u]:
                    return None                # an edge inside one side: odd cycle
    return colour

print(two_colour(4, [(0, 1), (1, 2), (2, 3), (3, 0)]))           # square
print(two_colour(3, [(0, 1), (1, 2), (2, 0)]))                   # triangle
print(two_colour(5, [(0, 1), (2, 3), (3, 4), (4, 2)]))           # triangle in the 2nd component
```
```text
[0, 1, 0, 1]
None
None
```

The third graph shows why the outer loop matters: a check that starts only from vertex `0` sees the edge `0-1`, finds no conflict, and wrongly says "bipartite". The odd cycle `2-3-4` lives in another component.

Cost: one BFS over everything, **`O(V + E)`**. DFS works just as well; only the colours matter, not the order.

**Predict the output.** Is a tree always bipartite? Is a grid graph (cells joined up/down/left/right) bipartite?

<details><summary>Answer</summary>

Both always are. A tree has no cycles at all, so no odd cycles; colour by depth (even depth red, odd depth blue). A grid is bipartite like a chess board: colour cell `(r, c)` by `(r + c) % 2`; every move changes `r + c` by one, so it changes the colour.

```python
tree_edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
print(two_colour(6, tree_edges))
```
```text
[0, 1, 1, 0, 0, 0]
```

</details>

## 9. Union-Find (disjoint set union)

### The problem: groups that keep merging

Edges arrive one by one: "Asha and Ben are now friends", "Ben and Chen are now friends". After each one, someone asks "are Asha and Chen in the same group?" Running a BFS for every question costs `O(V + E)` each time. **Union-Find** (also called **disjoint set union**, DSU) answers both operations in almost `O(1)`:

- `union(x, y)`: merge the groups of `x` and `y`,
- `find(x)`: return a **representative** of `x`'s group. Two vertices are in the same group exactly when they have the same representative.

### Each group is a tree

Every element points to a **parent** in its group; the **root** points to itself and is the representative. `find` walks up to the root. `union` finds both roots and makes one root point to the other.

```text
   after union(0,1), union(2,3), union(1,3):

        0            parent = [0, 0, 0, 2, 4]
       / \           find(3): 3 -> 2 -> 0, so the root is 0
      1   2          4 is alone in its own group
          |
          3
```

Done naively, the trees can become long chains, and `find` becomes `O(n)`. Two small tricks fix that:

1. **Union by size**: hang the **smaller** tree under the root of the **bigger** one. A vertex then moves one level deeper only when its group at least doubles in size, so no tree is taller than `log2 n`.
2. **Path compression**: after `find(x)` has found the root, make **every vertex on the path point straight to the root**. The next `find` on any of them takes one step.

```python
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))           # everyone starts as their own root
        self.size = [1] * n
        self.groups = n

    def find(self, x):
        root = x
        while self.parent[root] != root:       # walk up to the root
            root = self.parent[root]
        while self.parent[x] != root:          # path compression: point everyone at the root
            nxt = self.parent[x]
            self.parent[x] = root
            x = nxt
        return root

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False                       # already in the same group
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx                    # rx is the bigger root
        self.parent[ry] = rx                   # hang the smaller tree under the bigger
        self.size[rx] += self.size[ry]
        self.groups -= 1
        return True

d = DSU(5)
d.union(0, 1)
d.union(2, 3)
d.union(1, 3)
print("parent:", d.parent, " groups:", d.groups)
print("3 and 0 together?", d.find(3) == d.find(0), "  4 and 0?", d.find(4) == d.find(0))
print("union(0, 2) again:", d.union(0, 2))
```
```text
parent: [0, 0, 0, 2, 4]  groups: 2
3 and 0 together? True   4 and 0? False
union(0, 2) again: False
```

`find` is written with two loops, not recursion: a recursive `find` on a long chain (before compression flattens it) can hit the recursion limit.

### How much do the tricks save?

Make 100,000 unions along a line, `union(i, i + 1)`, with and without the tricks, and measure the tallest tree.

```python
def naive_parent_chain(n):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for i in range(n - 1):
        parent[find(i)] = find(i + 1)          # always hang the left root under the right one
    return parent

def depth(parent, x):
    steps = 0
    while parent[x] != x:
        x = parent[x]
        steps += 1
    return steps

n = 100_000
naive = naive_parent_chain(n)
good = DSU(n)
for i in range(n - 1):
    good.union(i, i + 1)
print("naive: depth of vertex 0 =", depth(naive, 0))
print("DSU  : largest depth     =", max(depth(good.parent, x) for x in range(n)))
```
```text
naive: depth of vertex 0 = 99999
DSU  : largest depth     = 1
```

The naive structure is a single chain: one `find(0)` walks 99,999 steps, and a few thousand such finds make the program hopeless. With union by size, every vertex is one step from the root here.

With both tricks, any sequence of `m` operations on `n` elements costs `O(m α(n))`, where `α` is the inverse Ackermann function. It grows so slowly that `α(n) ≤ 4` for any `n` you will ever store. In practice: **`O(1)` per operation**. With only one of the two tricks you still get `O(log n)`.

### Using it

**Cycle detection while adding edges.** In an undirected graph, the edge `u-v` closes a cycle exactly when `u` and `v` are already in the same group. The `union` method returns `False` in that case. This finds the first "redundant" edge:

```python
def redundant_edge(n, edge_list):
    d = DSU(n)
    for u, v in edge_list:
        if not d.union(u, v):
            return (u, v)                      # u and v were already connected
    return None

print(redundant_edge(4, [(0, 1), (1, 2), (2, 3), (3, 1), (0, 3)]))
print(redundant_edge(4, [(0, 1), (1, 2), (2, 3)]))
```
```text
(3, 1)
None
```

**Groups as edges arrive.** `d.groups` keeps the number of components after every edge, in `O(1)`:

```python
d = DSU(6)
history = []
for u, v in [(0, 1), (2, 3), (1, 0), (4, 5), (1, 3), (5, 3)]:
    d.union(u, v)
    history.append(d.groups)
print(history)
```
```text
[5, 4, 4, 3, 2, 1]
```

The edge `(1, 0)` repeats a connection, so the count does not drop.

**Merging records that share a key.** People sign up with several email addresses; two accounts with a shared address belong to the same person. Give every account a number, and union the accounts that share an email (remember, in a dictionary, the first account that used each email).

```python
def merge_accounts(accounts):
    d = DSU(len(accounts))
    owner = {}                                 # email -> first account index that had it
    for i, emails in enumerate(accounts):
        for e in emails:
            if e in owner:
                d.union(i, owner[e])
            else:
                owner[e] = i
    groups = defaultdict(set)
    for e, i in owner.items():
        groups[d.find(i)].add(e)
    return sorted(sorted(g) for g in groups.values())

accounts = [["a@x", "b@x"], ["c@x"], ["b@x", "d@x"], ["e@x", "c@x"], ["f@x"]]
for group in merge_accounts(accounts):
    print(group)
```
```text
['a@x', 'b@x', 'd@x']
['c@x', 'e@x']
['f@x']
```

### Union-Find or BFS?

| Situation | Better tool |
|---|---|
| the graph is given once, and you need components | BFS/DFS (`O(V + E)`) or DSU, both fine |
| edges **arrive over time**, questions in between | **DSU** |
| you need paths or distances, not just "same group?" | BFS/DFS (DSU forgets how things are connected) |
| edges are **removed** | neither directly; DSU cannot split a group. (Trick: if all removals are known in advance, process them backwards as additions.) |
| directed graphs | not DSU: it only models two-way connectivity |

**Traps.** Compare `find(x) == find(y)`, never `parent[x] == parent[y]` (two vertices can share a root without sharing a parent). Call `find` again after unions: a root stored earlier may no longer be a root. And remember that `union` must link **roots**, not the vertices themselves: `parent[x] = y` instead of `parent[find(x)] = find(y)` cuts `x` off from its old group.

## 10. Shortest paths with weights: Dijkstra

### Why BFS is not enough

BFS counts **edges**. Real roads have **lengths**. Look at this map (undirected, the numbers are kilometres):

```text
           4
     A ---------- B
     |          / |
   1 |      2 /   | 1
     |      /     |
     C ---------- D ---------- E
           5            3
```

The route with the fewest roads from `A` to `D` is `A B D`: two roads, `4 + 1 = 5` km. But `A C B D` uses three roads and is only `1 + 2 + 1 = 4` km. BFS would answer 5. We need an algorithm that adds up weights.

```python
def weighted_graph(edge_list, directed=False):
    adj = defaultdict(list)
    for u, v, w in edge_list:
        adj[u].append((v, w))
        if not directed:
            adj[v].append((u, w))
        else:
            adj[v]                             # touch v so that it exists as a key
    return adj

roads = [("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 1), ("C", "D", 5), ("D", "E", 3)]
city = weighted_graph(roads)
```

### The idea: settle the closest vertex first

Dijkstra's algorithm keeps a **tentative distance** `dist[v]` for every vertex: the length of the best route to `v` found so far (infinity at first, 0 for the source). Then it repeats:

1. Among the vertices not yet **settled**, take the one with the **smallest** tentative distance, `u`.
2. `u` is now settled: its distance is final.
3. **Relax** every edge `u -> v` with weight `w`: if `dist[u] + w < dist[v]`, we found a better route to `v`; lower `dist[v]` and remember `parent[v] = u`.

Why is the smallest tentative distance final? Suppose `dist[u] = d` is the smallest among the unsettled vertices. Any other route to `u` must leave the settled region through some unsettled vertex `x`, and `dist[x] >= d` already. The rest of that route adds weights that are **never negative**, so it cannot end below `d`. This argument is the whole reason Dijkstra needs **non-negative weights** (more on that below).

"Take the smallest, again and again, while values change" is exactly the job of a **heap** (dsa.11). Instead of changing a value inside the heap, we push a **new** entry `(new distance, v)` and leave the old one there. When an old entry reaches the top, its distance is larger than `dist[v]`, and we skip it. This is the **lazy deletion** of dsa.11, section 11.

```python
def dijkstra(adj, source, trace=False):
    dist = {v: float("inf") for v in adj}
    dist[source] = 0
    parent = {source: None}
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            if trace:
                print(f"pop ({d}, {u})  stale, skip")
            continue                           # an old entry: u was already settled
        if trace:
            print(f"pop ({d}, {u})  settle {u} at {d}")
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:                   # relax the edge u -> v
                dist[v] = nd
                parent[v] = u
                heapq.heappush(heap, (nd, v))
                if trace:
                    print(f"      {v}: {nd}  (via {u})")
    return dist, parent

dist, parent = dijkstra(city, "A", trace=True)
print(dist)
print(path_to(parent, "E"))
```
```text
pop (0, A)  settle A at 0
      B: 4  (via A)
      C: 1  (via A)
pop (1, C)  settle C at 1
      B: 3  (via C)
      D: 6  (via C)
pop (3, B)  settle B at 3
      D: 4  (via B)
pop (4, B)  stale, skip
pop (4, D)  settle D at 4
      E: 7  (via D)
pop (6, D)  stale, skip
pop (7, E)  settle E at 7
{'A': 0, 'B': 3, 'C': 1, 'D': 4, 'E': 7}
['A', 'C', 'B', 'D', 'E']
```

Read the trace slowly:

- `A` is settled at 0. Its edges give `B` the tentative distance 4 and `C` 1.
- `C` (1) is the smallest, so it is settled. Through `C`, `B` costs `1 + 2 = 3 < 4`: a better route, so `(3, B)` is pushed. The old `(4, B)` **stays in the heap**. `D` gets `1 + 5 = 6`.
- `B` is settled at 3. Through `B`, `D` costs `3 + 1 = 4 < 6`.
- `(4, B)` comes out: it is **stale** (4 is larger than `dist[B] = 3`), so it is skipped.
- `D` is settled at 4 and gives `E` the distance 7. The stale `(6, D)` is skipped. `E` is settled at 7.

`path_to` from section 3 works unchanged on the `parent` dictionary: `A C B D E`, 7 km.

### Complexity

Every edge can push at most one entry, so the heap holds at most `E + 1` entries, and every push and pop costs `O(log E) = O(log V)` (because `E ≤ V²`, `log E ≤ 2 log V`). Total: **`O((V + E) log V)`** time and `O(V + E)` memory.

For a **dense** graph (`E` close to `V²`), a version without a heap is better: keep `dist` in a list and find the smallest unsettled vertex by scanning, `O(V)` per step, `O(V²)` in total. That beats `O(V² log V)`. You will see the same idea in Prim's algorithm for dense graphs (section 15).

**Stop early** if you only need the distance to one target: return as soon as the target is **popped and settled** (not when it is first pushed; a better route may still come, as `B` showed above).

### Dijkstra and negative edges

The proof used "the rest of the route can only add". A negative edge breaks it. Here is a small directed graph:

```text
   S ---2---> A ---1---> T          the best route to A is S B A: 5 + (-4) = 1
   |          ^                     so the best route to T is 1 + 1 = 2
   5          | -4
   v          |
   B ---------+
```

The textbook form of Dijkstra keeps a `done` set: a settled vertex is never touched again. It settles `A` at 2 (the smallest at that moment), and when the edge `B -> A` with weight `-4` is found later, `A` is already done:

```python
def dijkstra_done_set(adj, source):
    dist = {v: float("inf") for v in adj}
    dist[source] = 0
    done = set()
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        for v, w in adj[u]:
            if v not in done and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist

neg = weighted_graph([("S", "A", 2), ("S", "B", 5), ("B", "A", -4), ("A", "T", 1)], directed=True)
print(dijkstra_done_set(neg, "S"))
```
```text
{'S': 0, 'A': 2, 'B': 5, 'T': 3}
```

`A` should be 1 and `T` should be 2. The answer is wrong.

Our lazy version (with `if d > dist[u]: continue`) happens to get this one right, because it lets `A` be "settled" a second time when its distance drops:

```python
pops = []
def counting_dijkstra(adj, source):
    dist = {v: float("inf") for v in adj}
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        pops.append(u)
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist

print(counting_dijkstra(neg, "S"))
print("vertices processed:", pops)
```
```text
{'S': 0, 'A': 1, 'B': 5, 'T': 2}
vertices processed: ['S', 'A', 'T', 'B', 'A', 'T']
```

But look at the second line: `A` and `T` were processed **twice**. The promise "each vertex is settled once" is gone. On bad graphs with negative edges the number of re-processings can grow **exponentially**, and with a **negative cycle** the loop never ends (each lap lowers the distances again). So the rule is simple: **negative edge weights → do not use Dijkstra.** Use Bellman-Ford (section 12).

(Adding a constant to every edge to make them all positive does **not** work either: a route with more edges gets a bigger penalty, so the shortest route can change.)

**Try it 5.** A signal is sent from server `1` of a network. `times` lists directed links `(u, v, t)`: the signal goes from `u` to `v` in `t` ms. How long until **every** server has the signal? Return `-1` if some server never gets it.

```text
times = [(2, 1, 1), (2, 3, 1), (3, 4, 1)], n = 4, start at 2   -> 2
times = [(1, 2, 1)], n = 2, start at 2                         -> -1
```

<details><summary>Answer</summary>

Every server receives the signal at its shortest-path distance, so the answer is the **largest** distance (or `-1` if one is infinite).

```python
def network_delay(times, n, start):
    adj = {v: [] for v in range(1, n + 1)}     # every server, even with no links
    for u, v, t in times:
        adj[u].append((v, t))
    dist, _ = dijkstra(adj, start)
    worst = max(dist.values())
    return -1 if worst == float("inf") else worst

print(network_delay([(2, 1, 1), (2, 3, 1), (3, 4, 1)], 4, 2))
print(network_delay([(1, 2, 1)], 2, 2))
```
```text
2
-1
```

Building `adj` for all `n` servers first matters: a server with no links at all must still count as "not reached".

</details>

## 11. 0-1 BFS

### When the weights are only 0 and 1

Some problems have edges that are either **free** (weight 0) or cost **one** unit. "Walk through open cells for free, but breaking a wall costs 1: what is the fewest walls you must break?" Dijkstra solves it in `O((V + E) log V)`. But there is a neat linear-time trick.

In BFS the queue holds distances `d, d, ..., d + 1, d + 1` in order. With 0-weight edges, a neighbour reached by a free edge has the **same** distance `d` as the current vertex, so it belongs at the **front** of the queue, not the back. A **deque** (dsa.08) allows both:

- edge weight 0: `appendleft` (same distance, handle it soon),
- edge weight 1: `append` (distance `d + 1`, after the current wave).

The deque then always holds distances `d ... d` followed by `d + 1 ... d + 1`, so it is sorted, and the front is always a smallest one, just like the top of Dijkstra's heap, at `O(1)` per operation.

```python
def min_walls(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    INF = float("inf")
    dist = [[INF] * cols for _ in range(rows)]
    dist[start[0]][start[1]] = 0
    dq = deque([start])
    while dq:
        r, c = dq.popleft()
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            w = 1 if grid[nr][nc] == "#" else 0    # entering a wall cell costs 1
            if dist[r][c] + w < dist[nr][nc]:
                dist[nr][nc] = dist[r][c] + w
                if w == 0:
                    dq.appendleft((nr, nc))
                else:
                    dq.append((nr, nc))
    return dist[goal[0]][goal[1]]

WALLS = ["..#...",
         "###.#.",
         "...#..",
         ".#####",
         "......"]
print(min_walls(WALLS, (0, 0), (4, 5)))
print(min_walls(WALLS, (0, 0), (2, 0)))
```
```text
1
1
```

Look at the grid: the start `(0, 0)` and `(0, 1)` are sealed in by the walls `(0, 2)`, `(1, 0)`, `(1, 1)` and `(1, 2)`. Breaking `(1, 0)` (cost 1) opens column 0, which is free from row 2 down to row 4, and row 4 is free all the way to the corner. So both targets cost exactly one broken wall.

### Things to know

- Unlike plain BFS, a vertex can be **improved after it was first reached** (first through a wall, later for free), so we compare distances (`dist[r][c] + w < dist[nr][nc]`) instead of a "seen" flag, as in Dijkstra. A vertex can enter the deque more than once, but each time with a smaller distance; it is processed a constant number of times. Cost: **`O(V + E)`**.
- It works for any graph whose weights are only `0` and `1` (or only `0` and some fixed `k`). For weights like `1` and `2`, either split each 2-edge into two 1-edges with a middle vertex, or use Dijkstra.
- If all weights are equal (all 1), 0-1 BFS is just BFS.

Typical disguises: "minimum number of direction changes / turns", "minimum cells to flip", "free moves along an arrow, a paid move against it".

## 12. Bellman-Ford: negative edges and negative cycles

### Relax every edge, again and again

Bellman-Ford takes the opposite approach to Dijkstra. It does not choose a clever order; it simply **relaxes every edge**, and repeats this whole round `V - 1` times.

Why `V - 1` rounds? A shortest path that does not repeat a vertex has at most `V - 1` edges. After round 1, every vertex whose best path has **one** edge has its final distance (the first edge of every path was relaxed). After round 2, every vertex whose best path has **two** edges is right, because its second-to-last vertex was already right after round 1, and its last edge was relaxed in round 2. And so on: after round `k`, all vertices whose best path uses at most `k` edges are correct. After `V - 1` rounds, all are.

Nothing in this argument cares whether a weight is negative. That is the point of Bellman-Ford.

```python
def bellman_ford(vertices, edge_list, source, show=False):
    INF = float("inf")
    dist = {v: INF for v in vertices}
    dist[source] = 0
    for rnd in range(1, len(vertices)):          # V - 1 rounds
        changed = False
        for u, v, w in edge_list:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if show:
            print(f"after round {rnd}:", dist)
        if not changed:
            break                                  # nothing moved: already final
    return dist

V5 = ["s", "t", "x", "y", "z"]
E5 = [("t", "x", 5), ("t", "y", 8), ("t", "z", -4), ("x", "t", -2), ("y", "x", -3),
      ("y", "z", 9), ("z", "x", 7), ("z", "s", 2), ("s", "t", 6), ("s", "y", 7)]
final = bellman_ford(V5, E5, "s", show=True)
```
```text
after round 1: {'s': 0, 't': 6, 'x': inf, 'y': 7, 'z': inf}
after round 2: {'s': 0, 't': 6, 'x': 4, 'y': 7, 'z': 2}
after round 3: {'s': 0, 't': 2, 'x': 4, 'y': 7, 'z': 2}
after round 4: {'s': 0, 't': 2, 'x': 4, 'y': 7, 'z': -2}
```

This is the classic example from Cormen et al. Read the edge list: there are three negative edges (`t -> z`, `x -> t`, `y -> x`), but no cycle with a negative total. The final distances are `t = 2` (via `s y x t`: `7 - 3 - 2`), `x = 4` (via `s y x`), `y = 7`, `z = -2` (via `s y x t z`).

The `dist[u] != INF` test stops "infinity minus 4" from looking like progress at a vertex that has not been reached yet. (`inf - 4` is still `inf` in Python, but with a large integer like `10**18` used as "infinity" it would not be, so the habit is worth keeping.)

Watch the rounds. Round 1 can only use the edges out of `s`. Round 2 finds `x` through `y`, round 3 finds the better `t` through `x`, and round 4 finds the better `z` through the new `t`. The best path to `z`, `s y x t z`, has four edges, and with this edge order each round extends it by one edge, so all `V - 1 = 4` rounds were needed. With the edges in a luckier order, fewer rounds would do; the final distances never depend on the order.

**Early exit:** if a whole round changes nothing, no later round can change anything either, so we stop early. On many inputs that saves most of the rounds.

Cost: `V - 1` rounds of `E` edges: **`O(V · E)`** time, `O(V)` memory. That is much slower than Dijkstra, which is why we use it only when we must.

### Detecting a negative cycle

A **negative cycle** is a cycle whose weights add up to less than zero. Going round it once more always makes the route shorter, so "the shortest path" does not exist for any vertex the cycle can reach: its distance is minus infinity.

After `V - 1` rounds, all real shortest paths are final. So if a **`V`-th round** can still improve some distance, there must be a negative cycle. To also find **which** vertices are affected, take every vertex that can still be improved and mark everything reachable from it as `-inf`.

```python
def bellman_ford_full(vertices, edge_list, source):
    INF = float("inf")
    dist = {v: INF for v in vertices}
    dist[source] = 0
    for _ in range(len(vertices) - 1):
        for u, v, w in edge_list:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    # one more round: whatever still improves is touched by a negative cycle
    bad = deque(v for u, v, w in edge_list if dist[u] != INF and dist[u] + w < dist[v])
    adj = defaultdict(list)
    for u, v, w in edge_list:
        adj[u].append(v)
    while bad:
        u = bad.popleft()
        if dist[u] == -INF:
            continue
        dist[u] = -INF
        bad.extend(adj[u])                     # everything reachable is also -inf
    return dist

cyc_edges = [("s", "a", 1), ("a", "b", 1), ("b", "c", -3), ("c", "a", 1), ("c", "d", 2), ("s", "e", 4)]
print(bellman_ford_full(["s", "a", "b", "c", "d", "e"], cyc_edges, "s"))
```
```text
{'s': 0, 'a': -inf, 'b': -inf, 'c': -inf, 'd': -inf, 'e': 4}
```

The cycle `a -> b -> c -> a` has total `1 - 3 + 1 = -1`. Every vertex on it, and `d` (reachable from it), is `-inf`. `s` and `e` are not reachable from the cycle and keep normal distances.

To answer only "does the graph have a negative cycle **anywhere**?" (not only one reachable from `s`), start with `dist[v] = 0` for **every** vertex. That is the same as adding a new source with a 0-weight edge to every vertex.

### Paths with at most `k` edges, and the copy trap

"Cheapest flight from `src` to `dst` with **at most `k` stops**" (at most `k + 1` flights) is Bellman-Ford with exactly `k + 1` rounds. But there is a trap. Inside one round, if we update `dist` in place, a distance improved early in the round can be used again later **in the same round**, so one round may extend a path by several edges. The round-counting argument breaks. The fix: in each round, read from a **copy** of the previous round's distances.

```python
def cheapest_within(n, flights, src, dst, k, use_copy=True):
    INF = float("inf")
    dist = [INF] * n
    dist[src] = 0
    for _ in range(k + 1):                     # at most k + 1 flights
        prev = dist[:] if use_copy else dist   # the copy is the whole trick
        for u, v, price in flights:
            if prev[u] != INF and prev[u] + price < dist[v]:
                dist[v] = prev[u] + price
    return -1 if dist[dst] == INF else dist[dst]

flights = [(0, 1, 100), (1, 2, 100), (0, 2, 500)]
print("0 stops, with copy   :", cheapest_within(3, flights, 0, 2, 0))
print("0 stops, without copy:", cheapest_within(3, flights, 0, 2, 0, use_copy=False))
print("1 stop,  with copy   :", cheapest_within(3, flights, 0, 2, 1))
```
```text
0 stops, with copy   : 500
0 stops, without copy: 200
1 stop,  with copy   : 200
```

With 0 stops only the direct flight (500) is allowed. Without the copy, the single round first sets `dist[1] = 100` and then immediately uses it for `1 -> 2`, a 2-flight route that the limit forbids. Cost: `O(k · E)`.

Note that plain Dijkstra cannot answer this question: the cheapest route may have too many stops, and the route it throws away (more expensive but with fewer stops) is the one you need. Dijkstra on the state `(city, flights used)` does work, at a larger cost.

### SPFA

You may meet **SPFA** ("shortest path faster algorithm"): Bellman-Ford that only re-relaxes the edges of vertices whose distance changed, kept in a queue. It is often fast on random data, but its worst case is still `O(V · E)`, and contest problems are often built to hit that worst case. Prefer Dijkstra when weights are non-negative.

## 13. Floyd-Warshall: all pairs at once

### Distances between every pair

Sometimes you need the distance between **every** pair of vertices: a distance table for a road atlas, "the city with the fewest neighbours within distance X", or many queries on a small graph. Running Dijkstra from every vertex costs `V · O((V + E) log V)`. For a small or dense graph, Floyd-Warshall is simpler: three nested loops and a `V x V` table.

### The idea: allow one more middle vertex each time

Number the vertices `0 .. V-1`. Let `dist_k[i][j]` be the shortest route from `i` to `j` that uses only vertices `0 .. k-1` **in the middle** (the ends can be anything). With no middle vertices allowed, `dist_0` is just the edge weights. When we also allow vertex `k` in the middle, the best route either does not use `k` (its length is unchanged), or goes `i -> ... -> k -> ... -> j`, where both halves use only `0 .. k-1`:

```text
dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

After all `V` vertices are allowed, `dist[i][j]` is the true shortest distance. We can update one table in place: in round `k`, the entries `dist[i][k]` and `dist[k][j]` do not change (going through `k` to reach `k` adds nothing, as long as there is no negative cycle).

```python
def floyd_warshall(n, edge_list):
    INF = float("inf")
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edge_list:
        dist[u][v] = min(dist[u][v], w)        # keep the cheaper of parallel edges
    for k in range(n):                         # the middle vertex: OUTERMOST loop
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist

def show_table(table):
    for row in table:
        print(" ".join(f"{'inf' if x == float('inf') else x:>4}" for x in row))

fw_edges = [(0, 1, 3), (0, 2, 8), (1, 2, 2), (2, 3, 1), (3, 0, 2), (1, 3, 7)]
show_table(floyd_warshall(4, fw_edges))
```
```text
   0    3    5    6
   5    0    2    3
   3    6    0    1
   2    5    7    0
```

Check one entry: `dist[0][3]`. Direct is impossible; `0 -> 1 -> 3` is `3 + 7 = 10`; but `0 -> 1 -> 2 -> 3` is `3 + 2 + 1 = 6`. The table says 6. And `dist[3][2] = 7` is `3 -> 0 -> 1 -> 2`: `2 + 3 + 2`.

Cost: **`O(V³)`** time, `O(V²)` memory. In Python that is fine up to a few hundred vertices (`V = 400` is 64 million steps: slow but possible); beyond that, use Dijkstra from each source. Negative edges are allowed.

### Trap: the order of the loops

The `k` loop **must be the outermost**. It is tempting to write `for i: for j: for k:`, which reads like "for each pair, try every middle vertex". But then, when the pair `(i, j)` is finished, the entries it needs (`dist[i][k]`, `dist[k][j]`) may not be final yet, and `(i, j)` is never looked at again.

```python
def floyd_wrong_order(n, edge_list):
    INF = float("inf")
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edge_list:
        dist[u][v] = min(dist[u][v], w)
    for i in range(n):
        for j in range(n):
            for k in range(n):                 # WRONG: k innermost
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist

trap_edges = [(0, 1, 1), (1, 0, 6), (2, 3, 2), (3, 1, 8)]
print("right order:", floyd_warshall(4, trap_edges)[2])
print("wrong order:", floyd_wrong_order(4, trap_edges)[2])
```
```text
right order: [16, 10, 0, 2]
wrong order: [inf, 10, 0, 2]
```

The route `2 -> 3 -> 1 -> 0` has length `2 + 8 + 6 = 16`. When the wrong version handles the pair `(2, 0)`, it needs `dist[2][1]`, which is filled later (when `j = 1`), so `dist[2][0]` stays infinite.

### Negative cycles and paths

- **Negative cycle:** after the algorithm, `dist[i][i] < 0` for some `i` means `i` is on a negative cycle (going round it beats staying put). Then the distances of pairs that can pass through such a vertex are meaningless.
- **Getting a path:** keep a table `nxt[i][j]`, the first step on the best route from `i` to `j`. Start with `nxt[u][v] = v` for each edge; when the route through `k` wins, set `nxt[i][j] = nxt[i][k]`.

```python
def floyd_with_paths(n, edge_list):
    INF = float("inf")
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[j if i == j else None for j in range(n)] for i in range(n)]
    for u, v, w in edge_list:
        if w < dist[u][v]:
            dist[u][v] = w
            nxt[u][v] = v
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]        # go towards k first
    return dist, nxt

def fw_path(nxt, i, j):
    if nxt[i][j] is None:
        return None
    path = [i]
    while i != j:
        i = nxt[i][j]
        path.append(i)
    return path

fw_dist, fw_nxt = floyd_with_paths(4, fw_edges)
print(fw_path(fw_nxt, 0, 3), fw_dist[0][3])
print(fw_path(fw_nxt, 3, 2), fw_dist[3][2])

neg_cycle = floyd_warshall(3, [(0, 1, 1), (1, 2, -2), (2, 1, 1)])
print("diagonal:", [neg_cycle[i][i] for i in range(3)])
```
```text
[0, 1, 2, 3] 6
[3, 0, 1, 2] 7
diagonal: [0, -1, -2]
```

The cycle `1 -> 2 -> 1` has total `-2 + 1 = -1`, so `dist[1][1]` and `dist[2][2]` are negative.

**Reachability for all pairs** (the *transitive closure*) is the same triple loop with booleans: `reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])`.

## 14. Which shortest-path algorithm?

The edge weights decide.

| Edge weights | Question | Algorithm | Time |
|---|---|---|---|
| none (every edge = 1 step) | from one source | **BFS** | `O(V + E)` |
| only 0 and 1 | from one source | **0-1 BFS** (deque) | `O(V + E)` |
| non-negative | from one source | **Dijkstra** (heap) | `O((V + E) log V)` |
| non-negative, dense graph | from one source | Dijkstra with an array scan | `O(V²)` |
| some negative, no negative cycle | from one source | **Bellman-Ford** | `O(V · E)` |
| some negative, cycles possible | detect / mark `-inf` | **Bellman-Ford** + one extra round | `O(V · E)` |
| at most `k` edges on the path | from one source | Bellman-Ford with `k` rounds and a copy | `O(k · E)` |
| any (no negative cycle), small `V` | **all pairs** | **Floyd-Warshall** | `O(V³)` |
| non-negative, large sparse graph | all pairs | Dijkstra from every vertex | `O(V (V + E) log V)` |
| a DAG, any weights | from one source | DP in topological order (section 7) | `O(V + E)` |

Questions to ask, in this order:

1. **Are all edges the same?** Then BFS. Never use Dijkstra where BFS is enough.
2. **Is the graph a DAG?** Then relax the edges in topological order: linear time, negative weights allowed, and it also gives **longest** paths.
3. **Any negative weight?** If not, Dijkstra (or 0-1 BFS for 0/1 weights). If yes, Bellman-Ford.
4. **One source or all pairs?** For all pairs on a small graph (`V` up to a few hundred), Floyd-Warshall.
5. **Extra limits** (at most `k` edges, a fuel tank, keys and doors)? Make the limit part of the **state**: the vertex becomes `(place, stops used)` or `(cell, keys held)`, and run BFS or Dijkstra on that bigger graph.

## 15. Minimum spanning trees

### Connecting everything as cheaply as possible

A town wants to connect six villages with cables. Each possible cable has a cost. Every village must be reachable from every other (directly or through others), and the total cost should be as small as possible. Extra cables that close a loop are wasted money: any cycle has one edge you could remove and still keep everything connected. So the answer is a **tree** that spans (touches) every vertex: a **minimum spanning tree** (MST). For `V` vertices it has exactly `V - 1` edges.

```text
         4          6
    A ------- B ------- C
    |       / |         |
  1 |    3/   | 5       | 2
    |   /     |         |
    D ------- E ------- F
         7         8
```

```python
cables = [("A", "B", 4), ("B", "C", 6), ("A", "D", 1), ("B", "D", 3),
          ("B", "E", 5), ("C", "F", 2), ("D", "E", 7), ("E", "F", 8)]
villages = ["A", "B", "C", "D", "E", "F"]
```

### The cut property: why greedy works

Split the vertices into any two groups (a **cut**). Some edges cross between the groups. **The cheapest crossing edge belongs to some MST.** Why: take any spanning tree without it. Adding the cheap edge makes a cycle; that cycle crosses the cut once with the cheap edge, so it must cross back with another crossing edge, which costs at least as much. Swap them: still a spanning tree, and no more expensive.

Both MST algorithms are greedy applications of this property. They differ in which cut they look at.

### Kruskal: cheapest edges first, skip the ones that close a cycle

Sort all edges by weight. Go through them from cheapest to most expensive, and take an edge if its two ends are **not yet connected**; otherwise it would close a cycle, so skip it. "Are they connected yet?" while edges are being added is exactly what Union-Find answers (section 9).

```python
def kruskal(vertices, edge_list):
    index = {v: i for i, v in enumerate(vertices)}
    d = DSU(len(vertices))
    tree, total = [], 0
    for u, v, w in sorted(edge_list, key=lambda e: e[2]):
        if d.union(index[u], index[v]):        # different groups: take the edge
            tree.append((u, v, w))
            total += w
            if len(tree) == len(vertices) - 1:
                break                          # a spanning tree is complete
        else:
            print(f"skip {u}-{v} ({w}): {u} and {v} are already connected")
    return tree, total

tree, total = kruskal(villages, cables)
print(tree)
print("total:", total)
```
```text
skip A-B (4): A and B are already connected
[('A', 'D', 1), ('C', 'F', 2), ('B', 'D', 3), ('B', 'E', 5), ('B', 'C', 6)]
total: 17
```

Trace: `A-D` (1), `C-F` (2) and `B-D` (3) join separate groups. `A-B` (4) would close the cycle `A B D`, so it is skipped. `B-E` (5) is taken, and `B-C` (6) joins the group `{A, B, D, E}` to `{C, F}`. That makes 5 edges for 6 vertices, so we stop; `D-E` (7) and `E-F` (8) are never even looked at.

Cost: sorting is **`O(E log E)`**, and the DSU work is almost `O(E)`. So Kruskal is `O(E log E)`, which is the same as `O(E log V)`.

If the graph is **not connected**, no spanning tree exists. Kruskal then returns a minimum spanning **forest** with fewer than `V - 1` edges; check `len(tree) == V - 1` before you claim "everything is connected".

### Prim: grow one tree from a start vertex

Prim's algorithm grows a single tree. The cut is "the tree so far" against "everything else", and each step adds the **cheapest edge leaving the tree**. A heap holds the candidate edges, and, as in Dijkstra, entries for vertices that are already in the tree are skipped when they come out.

```python
def prim(adj, start):
    in_tree = {start}
    heap = [(w, start, v) for v, w in adj[start]]
    heapq.heapify(heap)
    tree, total = [], 0
    while heap and len(in_tree) < len(adj):
        w, u, v = heapq.heappop(heap)
        if v in in_tree:
            continue                           # stale: v joined the tree already
        in_tree.add(v)
        tree.append((u, v, w))
        total += w
        for x, wx in adj[v]:
            if x not in in_tree:
                heapq.heappush(heap, (wx, v, x))
    return tree, total

cable_graph = weighted_graph(cables)
print(prim(cable_graph, "A"))
```
```text
([('A', 'D', 1), ('D', 'B', 3), ('B', 'E', 5), ('B', 'C', 6), ('C', 'F', 2)], 17)
```

Same total, 17, and the same edges (this graph has all-different weights, so its MST is unique), found in a different order: Prim grows outward from `A`.

Prim looks almost exactly like Dijkstra. The one difference: Dijkstra's heap key is the **whole distance from the source** (`d + w`); Prim's key is the **single edge weight** `w`. Cost with a heap: **`O(E log V)`**.

### Dense graphs: Prim without a heap

"Connect all `n` points on a plane; the cost of joining two points is their Manhattan distance `|x1 - x2| + |y1 - y2|`." Every pair is an edge: `E = n(n - 1) / 2`. Sorting all of them for Kruskal is `O(n² log n)` and needs all pairs in memory. Prim with a plain list is `O(n²)` with `O(n)` memory: keep `best[v]`, the cheapest edge from the tree to `v`, and each step pick the smallest by scanning.

```python
def connect_points(points):
    n = len(points)
    INF = float("inf")
    best = [INF] * n
    best[0] = 0
    in_tree = [False] * n
    total = 0
    for _ in range(n):
        u = min((i for i in range(n) if not in_tree[i]), key=lambda i: best[i])
        in_tree[u] = True
        total += best[u]
        ux, uy = points[u]
        for v in range(n):
            if not in_tree[v]:
                cost = abs(ux - points[v][0]) + abs(uy - points[v][1])
                if cost < best[v]:
                    best[v] = cost
    return total

print(connect_points([(0, 0), (2, 2), (3, 10), (5, 2), (7, 0)]))
print(connect_points([(3, 12), (-2, 5), (-4, 1)]))
```
```text
20
18
```

| | Kruskal | Prim (heap) | Prim (array) |
|---|---|---|---|
| idea | cheapest edge that joins two groups | cheapest edge leaving the tree | same, scan instead of heap |
| needs | edge list + DSU | adjacency list + heap | any way to get a weight |
| time | `O(E log E)` | `O(E log V)` | `O(V²)` |
| best for | sparse graphs, edges given as a list | sparse graphs, adjacency lists | dense / complete graphs |

### Trap: an MST is not a shortest-path tree

The MST minimises the **total** cost of the network. It does not give the shortest route between two vertices.

```python
tri = [("A", "B", 2), ("B", "C", 2), ("A", "C", 3)]
print("MST:", kruskal(["A", "B", "C"], tri))
print("shortest A -> C:", dijkstra(weighted_graph(tri), "A")[0]["C"])
```
```text
MST: ([('A', 'B', 2), ('B', 'C', 2)], 4)
shortest A -> C: 3
```

The MST connects `A` and `C` through `B` (a route of length 4), while the direct edge (length 3) is the shortest route. If the problem says "the cheapest network", think MST. If it says "the fastest way from X to Y", think shortest paths.

Two more facts worth knowing:

- A **maximum** spanning tree is Kruskal with the edges sorted from largest to smallest.
- In an MST, the path between two vertices has the **smallest possible largest edge** of any path between them (the *minimax* or *bottleneck* path). "Find the route whose worst road is as good as possible" is an MST question in disguise.

## 16. Strongly connected components

### Components in a directed graph

In a directed graph, "connected" splits into two ideas. `u` can reach `v` does not mean `v` can reach `u`. A **strongly connected component** (SCC) is a largest group of vertices in which **every vertex can reach every other**, following the arrows.

```text
    0 ---> 1          3 ---> 4          6 <---> 7
    ^      |          ^      |          |
    |      v          |      v          |
    +----- 2 -------> +----- 5 <--------+

    edges: 0->1, 1->2, 2->0, 2->3, 3->4, 4->5, 5->3, 6->5, 6->7, 7->6
    SCCs : {0, 1, 2}   {3, 4, 5}   {6, 7}
```

`{0, 1, 2}` go round in a circle, so they are one SCC. From `2` we can reach `3`, but `3` cannot come back, so `3` is in a different SCC.

If we shrink every SCC to a single vertex, we get the **condensation**, and it is always a **DAG** (if two SCCs could reach each other, they would be one SCC). This is very useful: many problems on a general directed graph become "first find the SCCs, then work on the DAG" (topological order, DP, counting sources).

```python
scc_graph = {0: [1], 1: [2], 2: [0, 3], 3: [4], 4: [5], 5: [3], 6: [5, 7], 7: [6]}
```

### Kosaraju's algorithm: two passes

1. Run DFS over the whole graph and record the vertices in the order they **finish**.
2. **Reverse** every edge.
3. Take the vertices in order of **decreasing finish time**. Each one that is not yet assigned starts a DFS in the **reversed** graph; everything that DFS reaches is one SCC.

Why does it work? The vertex that finishes last lies in a **source** SCC of the condensation (nothing outside points into it: otherwise the DFS would have entered from there and finished that part later). In the reversed graph, that source becomes a **sink**: a DFS from it cannot leave its SCC, so it collects exactly that SCC. Remove it, and the argument repeats with the next unassigned vertex.

```python
def finish_order(graph):
    seen, order = set(), []
    for s in graph:
        if s in seen:
            continue
        seen.add(s)
        stack = [(s, iter(graph[s]))]
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                order.append(u)                # u finishes
                stack.pop()
            elif v not in seen:
                seen.add(v)
                stack.append((v, iter(graph[v])))
    return order

def kosaraju(graph):
    reverse = {u: [] for u in graph}
    for u in graph:
        for v in graph[u]:
            reverse[v].append(u)
    comp = {}
    sccs = []
    for s in reversed(finish_order(graph)):    # latest finish first
        if s in comp:
            continue
        group = [s]
        comp[s] = len(sccs)
        stack = [s]
        while stack:                           # plain DFS in the reversed graph
            u = stack.pop()
            for v in reverse[u]:
                if v not in comp:
                    comp[v] = len(sccs)
                    group.append(v)
                    stack.append(v)
        sccs.append(sorted(group))
    return sccs, comp

print(finish_order(scc_graph))
sccs, comp = kosaraju(scc_graph)
print(sccs)
```
```text
[5, 4, 3, 2, 1, 0, 7, 6]
[[6, 7], [0, 1, 2], [3, 4, 5]]
```

The last vertex to finish is `6`, so its SCC `{6, 7}` is a source of the condensation (nothing points into it). Collected in the reversed graph, the SCCs come out in a **topological order of the condensation**: `{6, 7}`, then `{0, 1, 2}`, then `{3, 4, 5}`, which every arrow respects.

Cost: two DFS passes and building the reversed graph: **`O(V + E)`**. Written with stacks, it has no recursion-limit problem.

### Tarjan's algorithm: one pass with low-links

Tarjan's algorithm finds the SCCs in a single DFS. Each vertex gets:

- `index[u]`: the order in which DFS **entered** `u` (0, 1, 2, ...),
- `low[u]`: the smallest index reachable from `u`'s DFS subtree using at most one edge back to a vertex that is **still on the stack** (not yet assigned to an SCC).

Vertices are pushed on a stack when entered. When DFS finishes `u` and `low[u] == index[u]`, nothing below `u` can reach above `u`: `u` is the **root** (first vertex entered) of an SCC, and the SCC is everything on the stack from the top down to `u`.

```python
def tarjan(graph):
    index, low = {}, {}
    stack, on_stack = [], set()
    sccs = []

    def visit(u):
        index[u] = low[u] = len(index)         # entering order: 0, 1, 2, ...
        stack.append(u)
        on_stack.add(u)
        for v in graph[u]:
            if v not in index:                 # tree edge: go down
                visit(v)
                low[u] = min(low[u], low[v])
            elif v in on_stack:                # edge back into the current SCC candidate
                low[u] = min(low[u], index[v])
        if low[u] == index[u]:                 # u is the root of an SCC: pop it
            group = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                group.append(w)
                if w == u:
                    break
            sccs.append(sorted(group))

    for u in graph:
        if u not in index:
            visit(u)
    return sccs, index, low

t_sccs, t_index, t_low = tarjan(scc_graph)
print(t_sccs)
print("index:", t_index)
print("low  :", t_low)
```
```text
[[3, 4, 5], [0, 1, 2], [6, 7]]
index: {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
low  : {0: 0, 1: 0, 2: 0, 3: 3, 4: 3, 5: 3, 6: 6, 7: 6}
```

Follow vertex `3`: entered with index 3, then `4` (index 4) and `5` (index 5). The edge `5 -> 3` goes to a vertex on the stack, so `low[5] = 3`; that flows back up, `low[4] = 3`. At `3`, `low[3] == index[3] == 3`, so `{3, 4, 5}` is popped as one SCC, before `{0, 1, 2}` is finished. Tarjan emits the SCCs in **reverse** topological order of the condensation (sinks first).

Why the `on_stack` test? An edge to a vertex that is already in a **finished** SCC (like `6 -> 5`, found later) must be ignored: that SCC is closed, and `6` cannot belong to it.

This version is recursive, so it hits the recursion limit on deep graphs (section 4). For large inputs, use Kosaraju with stacks as above, or rewrite Tarjan with the iterator stack.

| | Kosaraju | Tarjan |
|---|---|---|
| passes | two DFS, plus a reversed graph | one DFS |
| extra memory | the reversed graph | index, low, the stack |
| easy without recursion | yes | possible, more fiddly |
| SCC order produced | topological (sources first) | reverse topological (sinks first) |
| time | `O(V + E)` | `O(V + E)` |

### Using the condensation

Build the DAG of SCCs: one vertex per SCC, and an edge between two SCCs whenever an original edge crosses between them.

```python
def condensation(graph, comp):
    dag_edges = set()
    for u in graph:
        for v in graph[u]:
            if comp[u] != comp[v]:
                dag_edges.add((comp[u], comp[v]))
    return sorted(dag_edges)

print(condensation(scc_graph, comp))
```
```text
[(0, 2), (1, 2)]
```

With Kosaraju's numbering, `0` is `{6, 7}`, `1` is `{0, 1, 2}` and `2` is `{3, 4, 5}`.

**Try it 6.** A rumour starts at some people and spreads along the arrows ("`u` tells `v`"). What is the smallest number of people you must tell yourself so that **everyone** hears it? Answer for `scc_graph`.

<details><summary>Answer</summary>

Inside an SCC everyone reaches everyone, so it is enough to tell one person per SCC that **nobody outside points into**: the SCCs with in-degree 0 in the condensation. Every other SCC is reached from one of those.

```python
def min_starters(graph):
    sccs, comp = kosaraju(graph)
    has_incoming = [False] * len(sccs)
    for a, b in condensation(graph, comp):
        has_incoming[b] = True
    return [sccs[c] for c in range(len(sccs)) if not has_incoming[c]]

starters = min_starters(scc_graph)
print(len(starters), starters)
```
```text
2 [[6, 7], [0, 1, 2]]
```

Two people: one from `{0, 1, 2}` and one from `{6, 7}`. `{3, 4, 5}` hears it from either of them.

</details>

## 17. Bridges and articulation points

### Weak spots in a network

In an undirected network:

- a **bridge** is an edge whose removal **disconnects** the graph (splits a component into two),
- an **articulation point** (cut vertex) is a vertex whose removal, together with its edges, disconnects the graph.

They are the single points of failure: the one cable, the one router, the one road.

```text
    0 --- 1 --- 3 --- 4 --- 5          bridges: 1-3, 3-4, 6-7
     \   /             \   /           articulation points: 1, 3, 4, 6
       2                 6 --- 7
```

The edges of a cycle are never bridges: remove one and you can go round the other way. `1-3` is a bridge because no cycle passes through it.

The slow way is to remove each edge and count the components again: `O(E · (V + E))`. Low-link values do it in **one DFS**, `O(V + E)`.

### Low-link values

Run DFS and give each vertex its entry time `tin[u]`. Define

`low[u]` = the smallest `tin` that can be reached from `u`'s DFS subtree, using tree edges down and **at most one non-tree edge** back up.

In an undirected DFS, every non-tree edge goes from a vertex to one of its **ancestors** (a "back edge"); there are no cross edges. So `low[u]` tells how high above `u` the subtree of `u` can climb without using the tree edge into `u`.

Then for a tree edge `u -> v` (`v` a child of `u`):

- **Bridge** if `low[v] > tin[u]`: nothing in `v`'s subtree can climb to `u` or above, so the edge `u-v` is the only connection.
- **Articulation point** at `u` (if `u` is not the root) if `low[v] >= tin[u]` for **some** child `v`: `v`'s subtree can climb at most to `u` itself, so removing `u` cuts it off.
- **The root** of the DFS is an articulation point exactly when it has **two or more** DFS children (with no parent above it, the rule above does not apply: its subtrees can only meet through it).

Notice the difference: `>` for bridges, `>=` for articulation points. A back edge to `u` itself saves the edge `u-v` (there is a cycle through it) but does not save the vertex `u`.

```python
def bridges_and_points(n, edge_list):
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edge_list):
        adj[u].append((v, i))
        adj[v].append((u, i))
    tin, low = [-1] * n, [0] * n
    bridges, points = [], set()
    timer = 0

    def visit(u, via):                         # via = index of the edge we came by
        nonlocal timer
        tin[u] = low[u] = timer
        timer += 1
        children = 0
        for v, i in adj[u]:
            if i == via:
                continue                       # skip only THIS edge, not every edge to the parent
            if tin[v] != -1:
                low[u] = min(low[u], tin[v])   # back edge
            else:
                children += 1
                visit(v, i)
                low[u] = min(low[u], low[v])
                if low[v] > tin[u]:
                    bridges.append(edge_list[i])
                if via != -1 and low[v] >= tin[u]:
                    points.add(u)
        if via == -1 and children >= 2:
            points.add(u)                      # the root rule

    for s in range(n):
        if tin[s] == -1:
            visit(s, -1)
    return bridges, sorted(points), tin, low

net = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 6), (6, 4), (6, 7)]
b, p, tin, low = bridges_and_points(8, net)
print("bridges:", b)
print("points :", p)
print("tin    :", tin)
print("low    :", low)
```
```text
bridges: [(6, 7), (3, 4), (1, 3)]
points : [1, 3, 4, 6]
tin    : [0, 1, 2, 3, 4, 5, 6, 7]
low    : [0, 0, 0, 3, 4, 4, 4, 7]
```

(`nonlocal timer` lets the inner function change the counter of the outer one; a one-item list `timer = [0]` is the other common way.)

Read the tables. `low[3] = 3 = tin[3]`: the subtree of `3` (vertices `3 .. 7`) cannot climb above `3`, and `3 > tin[1] = 1`, so `1-3` is a bridge and `1` is an articulation point. `low[2] = 0`: the back edge `2-0` lifts it to the root, so `0-1` and `1-2` are not bridges. `low[7] = 7 > tin[6] = 6`, so `6-7` is a bridge, and `6` is an articulation point.

### Check against the slow way

```python
def count_components(n, edge_list, removed_vertex=None):
    d = DSU(n)
    for u, v in edge_list:
        if removed_vertex not in (u, v):
            d.union(u, v)
    return d.groups - (1 if removed_vertex is not None else 0)

base = count_components(8, net)
slow_bridges = [e for e in net if count_components(8, [f for f in net if f != e]) > base]
slow_points = [x for x in range(8) if count_components(8, net, removed_vertex=x) > base]
print(sorted(slow_bridges) == sorted(b), slow_points == p)
```
```text
True True
```

(When a vertex is removed, the DSU still counts it as a group of its own, so we subtract one.)

### Trap: parallel edges and the parent check

Many versions you will find online skip "the edge back to the parent **vertex**". With a doubled edge that is wrong: two cables between `1` and `3` mean that cutting one still leaves the other, so `1-3` is no longer a bridge.

```python
def bridges_parent_vertex(n, edge_list):
    adj = [[] for _ in range(n)]
    for u, v in edge_list:
        adj[u].append(v)
        adj[v].append(u)
    tin, low, found = [-1] * n, [0] * n, []
    timer = 0
    def visit(u, parent):
        nonlocal timer
        tin[u] = low[u] = timer
        timer += 1
        for v in adj[u]:
            if v == parent:
                continue                       # skips BOTH copies of a doubled edge
            if tin[v] != -1:
                low[u] = min(low[u], tin[v])
            else:
                visit(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > tin[u]:
                    found.append((u, v))
    visit(0, -1)
    return found

doubled = net + [(1, 3)]
print("parent-vertex check:", bridges_parent_vertex(8, doubled))
print("edge-index check   :", bridges_and_points(8, doubled)[0])
```
```text
parent-vertex check: [(6, 7), (3, 4), (1, 3)]
edge-index check   : [(6, 7), (3, 4)]
```

The edge-index version correctly drops `1-3`. If the input promises no parallel edges, the parent check is fine; if it does not promise it, skip by edge index.

### Without recursion

A chain of 100,000 vertices has 99,999 bridges and would crash the recursive version. The iterative version uses the iterator stack of section 4. When a vertex `u` is finished, we update its parent's `low` and check the bridge condition on the edge between them.

```python
def bridges_iterative(n, edge_list):
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edge_list):
        adj[u].append((v, i))
        adj[v].append((u, i))
    tin, low = [-1] * n, [0] * n
    timer, found = 0, []
    for s in range(n):
        if tin[s] != -1:
            continue
        tin[s] = low[s] = timer
        timer += 1
        stack = [(s, -1, iter(adj[s]))]
        while stack:
            u, via, it = stack[-1]
            step = next(it, None)
            if step is None:                   # u is finished
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    low[p] = min(low[p], low[u])
                    if low[u] > tin[p]:
                        found.append(edge_list[via])
                continue
            v, i = step
            if i == via:
                continue
            if tin[v] == -1:
                tin[v] = low[v] = timer
                timer += 1
                stack.append((v, i, iter(adj[v])))
            else:
                low[u] = min(low[u], tin[v])
    return found

print(sorted(bridges_iterative(8, net)) == sorted(b))
long_chain = [(i, i + 1) for i in range(99_999)]
print(len(bridges_iterative(100_000, long_chain)))
```
```text
True
99999
```

**Bridges and SCCs side by side.** Both use the same `low` idea. In a directed graph, `low` finds where a strongly connected group starts (section 16). In an undirected graph, it finds where a 2-edge-connected (bridge-free) group ends. If you remove all bridges, the remaining components are the "2-edge-connected components", and shrinking each to one vertex turns the graph into a tree (the *bridge tree*).

## 18. Modelling a word problem as a graph

Most graph problems do not say "graph". The hard part is to see the graph. Ask four questions:

1. **What are the vertices?** Places, people, words, cells, states of a puzzle, variables.
2. **What are the edges?** "can move from ... to ...", "depends on", "is equal to", "differs by one letter". Directed or undirected? Weighted?
3. **What is asked?** Reachable? Fewest steps? Cheapest? An order? Groups? A weak spot?
4. **How big is it?** `V` and `E` decide between `O(V + E)`, `O((V + E) log V)`, `O(V · E)` and `O(V³)`. Do not build an edge list of a graph you can describe with a neighbour function.

### Example 1: word ladder (BFS on an implicit graph)

Change `"hit"` into `"cog"` one letter at a time, every word in between must be in the word list. Fewest words in the chain?

- vertices: the words; edges: words that differ in one letter; unweighted; asked: fewest steps → **BFS**.
- Comparing every pair of words is `O(N² · L)`. Faster: put each word into "buckets" with one letter replaced by `*` (`"hot"` goes into `"*ot"`, `"h*t"`, `"ho*"`). Two words are neighbours exactly when they share a bucket.

```python
def ladder_length(begin, end, words):
    buckets = defaultdict(list)
    for w in words:
        for i in range(len(w)):
            buckets[w[:i] + "*" + w[i + 1:]].append(w)
    dist = {begin: 1}                          # counting words, so the start is 1
    queue = deque([begin])
    while queue:
        w = queue.popleft()
        if w == end:
            return dist[w]
        for i in range(len(w)):
            key = w[:i] + "*" + w[i + 1:]
            for nxt in buckets[key]:
                if nxt not in dist:
                    dist[nxt] = dist[w] + 1
                    queue.append(nxt)
            buckets[key] = []                  # a bucket never needs to be scanned twice
    return 0

word_list = ["hot", "dot", "dog", "lot", "log", "cog"]
print(ladder_length("hit", "cog", word_list))
print(ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]))
```
```text
5
0
```

`hit -> hot -> dot -> dog -> cog` is five words. Emptying a bucket after the first scan is safe: every word in it was given a distance at that moment, and a later scan could not do better.

### Example 2: equations as a weighted graph

Given `a / b = 2` and `b / c = 3`, what is `a / c`? And `c / a`? And `a / x`?

- vertices: the variables; an equation `u / v = k` gives an edge `u -> v` with weight `k` **and** `v -> u` with weight `1 / k`. Following a path multiplies: `a / c = (a / b) * (b / c)`.
- asked: is there a path, and what is the product along it → BFS or DFS, carrying a product instead of a distance.

```python
def evaluate(equations, values, queries):
    adj = defaultdict(list)
    for (u, v), k in zip(equations, values):
        adj[u].append((v, k))
        adj[v].append((u, 1 / k))
    answers = []
    for start, goal in queries:
        if start not in adj or goal not in adj:
            answers.append(-1.0)               # an unknown variable
            continue
        product = {start: 1.0}
        queue = deque([start])
        while queue and goal not in product:
            u = queue.popleft()
            for v, k in adj[u]:
                if v not in product:
                    product[v] = product[u] * k
                    queue.append(v)
        answers.append(product.get(goal, -1.0))
    return answers

print(evaluate([("a", "b"), ("b", "c")], [2.0, 3.0],
               [("a", "c"), ("c", "a"), ("b", "a"), ("a", "x"), ("x", "x")]))
```
```text
[6.0, 0.16666666666666666, 0.5, -1.0, -1.0]
```

`c / a` comes out as `0.16666666666666666` because of floating-point rounding (dsa.02). `x / x` is `-1.0`, not `1.0`, because `x` appears in no equation: nothing is known about it.

### Example 3: an alien alphabet (topological sort)

A list of words is sorted in an unknown alphabet. Find an order of the letters.

- vertices: letters; edges: compare each pair of **neighbouring** words; the first position where they differ gives "letter `a` comes before letter `b`", a directed edge. Asked: an order that respects all edges → **topological sort**. A cycle means the input is contradictory.
- Trap: if a word is followed by its own **prefix** (`"abc"` before `"ab"`), the list cannot be sorted in any alphabet.

```python
def alien_order(words):
    letters = []
    for w in words:
        for ch in w:
            if ch not in letters:
                letters.append(ch)
    rules = set()
    for w1, w2 in zip(words, words[1:]):
        for a, c in zip(w1, w2):
            if a != c:
                rules.add((a, c))              # only the FIRST difference tells us anything
                break
        else:
            if len(w1) > len(w2):
                return None                    # "abc" before "ab": impossible
    order = kahn(letters, sorted(rules))
    return "".join(order) if order else None

print(alien_order(["wrt", "wrf", "er", "ett", "rftt"]))
print(alien_order(["z", "x", "z"]))
print(alien_order(["abc", "ab"]))
```
```text
wertf
None
None
```

`["z", "x", "z"]` says `z` before `x` and `x` before `z`: a cycle, so Kahn returns `None`. (The `for ... else` runs the `else` part only when the loop did not `break`, that is, when one word is a prefix of the other.)

### Example 4: a state graph with a limit

"Fewest steps through a grid from the top-left to the bottom-right corner, where you may remove at most `k` obstacles." The cell alone is not enough as a vertex: reaching the same cell with more removals left is better. So the vertex is the **state** `(row, col, removals left)`, and BFS runs on that bigger graph of `R · C · (k + 1)` states. The same trick handles "keys and doors", "fuel left", "stops used" (section 12): **whatever limits the future must be part of the state.**

```python
def shortest_with_removals(grid, k):
    rows, cols = len(grid), len(grid[0])
    start = (0, 0, k)
    dist = {start: 0}
    queue = deque([start])
    while queue:
        r, c, left = queue.popleft()
        if (r, c) == (rows - 1, cols - 1):
            return dist[(r, c, left)]
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols:
                nleft = left - (grid[nr][nc] == "#")
                state = (nr, nc, nleft)
                if nleft >= 0 and state not in dist:
                    dist[state] = dist[(r, c, left)] + 1
                    queue.append(state)
    return -1

OBST = ["...",
        "##.",
        "...",
        ".##",
        "..."]
print(shortest_with_removals(OBST, 1), shortest_with_removals(OBST, 0))
```
```text
6 10
```

With one removal, the route right, right, down, down, then through the wall at `(3, 2)` and down to the corner takes 6 steps: the Manhattan distance, which no route can beat. Without removals, the only route snakes right, down, left, down and right again: 10 steps.

## 19. Which algorithm for which problem?

| Clue in the problem | Model | Algorithm | Time |
|---|---|---|---|
| "can X reach Y?", "is it connected?" | any graph | BFS or DFS | `O(V + E)` |
| "fewest moves / steps / changes" | unweighted (or implicit state graph) | **BFS** | `O(V + E)` |
| "nearest X from every cell", several starts | grid | multi-source BFS | `O(V + E)` |
| "how many groups / islands / circles" | undirected | BFS/DFS over all starts, or DSU | `O(V + E)` |
| groups merge over time, "are they connected now?" | undirected, dynamic | **Union-Find** | `≈ O(1)` each |
| "in what order", prerequisites, build order | directed | **topological sort** (Kahn or DFS) | `O(V + E)` |
| "is it possible to finish?" with dependencies | directed | cycle detection (three colours / Kahn) | `O(V + E)` |
| "cycle?" in an undirected graph | undirected | parent check, DSU, or `E > V - C` | `O(V + E)` |
| "split into two groups with no conflicts" | undirected | **bipartite check** (2-colouring) | `O(V + E)` |
| longest / critical path, count paths, DP | DAG | DP in topological order | `O(V + E)` |
| "cheapest / shortest route" | weighted | see the table in section 14 | |
| "connect everything at minimum total cost" | weighted undirected | **MST**: Kruskal or Prim | `O(E log V)` |
| "route whose worst edge is best" | weighted undirected | MST path, or modified Dijkstra | `O(E log V)` |
| "groups where everyone reaches everyone", "mutual" | directed | **SCC** (Kosaraju / Tarjan) | `O(V + E)` |
| "which link / node is critical?" | undirected | **bridges / articulation points** | `O(V + E)` |
| limits like k stops, keys, fuel | any | put the limit into the **state** | states × moves |

And the shortest-path choice, once more, by edge weights:

| Edge weights | One source | All pairs |
|---|---|---|
| all equal | BFS | BFS from each vertex, `O(V (V + E))` |
| only 0 and 1 | 0-1 BFS | 0-1 BFS from each vertex |
| non-negative | Dijkstra | Dijkstra from each vertex, or Floyd-Warshall for small `V` |
| negative, no negative cycle | Bellman-Ford (or DAG DP if acyclic) | Floyd-Warshall |
| negative cycles possible | Bellman-Ford + extra round to detect | Floyd-Warshall, check `dist[i][i] < 0` |

## 20. Common traps, collected

1. **No visited set.** On any graph with a cycle the search never ends; on a DAG it repeats work exponentially.
2. **BFS marking on pop instead of push.** Vertices enter the queue many times: correct but slow, sometimes out of memory.
3. **Undirected edges stored in one direction only**, or a directed edge stored in both.
4. **Isolated vertices forgotten** because the graph was built only from the edge list; components and "unreachable" answers come out wrong.
5. **`[[]] * n`** for adjacency lists: every vertex shares one list.
6. **Starting only from vertex 0** in components, bipartite checks, cycle checks, topological sort: other components are never examined.
7. **Recursive DFS on a deep graph:** `RecursionError` at depth about 1,000. Raising the limit can crash the interpreter. Use a stack.
8. **The undirected cycle check on a directed graph** (the diamond looks cyclic), or the three-colour check on an undirected graph (every edge looks like a cycle).
9. **Topological sort without cycle detection:** Kahn's order is shorter than `V` when there is a cycle; check it.
10. **Comparing a "valid order" with one fixed answer.** Many topological orders are correct.
11. **BFS for weighted shortest paths.** Fewest edges is not least weight.
12. **Dijkstra with negative edges.** Wrong answers (with a `done` set) or exponential time / an endless loop (lazy version). Use Bellman-Ford.
13. **Stopping Dijkstra when the target is pushed** instead of when it is popped.
14. **Forgetting the stale-entry check** `if d > dist[u]: continue`: the algorithm is still correct but re-relaxes the edges of a vertex many times.
15. **Bellman-Ford with `k` limits updating in place:** one round can use several edges. Read from a copy of the previous round.
16. **Floyd-Warshall with `k` not the outermost loop.**
17. **Using "infinity" carelessly:** `INF + w` with a big integer stand-in, or comparing with `-inf` after negative cycles. Skip unreached vertices with `if dist[u] != INF`.
18. **DSU: comparing parents instead of roots**, linking non-root vertices, or a recursive `find` on a long chain.
19. **MST confused with shortest paths.** The MST minimises the total, not each route.
20. **Kruskal on a disconnected graph** reported as a spanning tree: check that it has `V - 1` edges.
21. **Tarjan: forgetting the `on_stack` test**, so an edge into an already finished SCC lowers `low` wrongly.
22. **Bridges: skipping every edge to the parent vertex** when parallel edges are possible; and using `>=` (articulation points) where `>` (bridges) is needed, or the reverse; and forgetting the root rule for articulation points.
23. **1-based input mixed with 0-based lists.** Off-by-one vertices, or an `IndexError` on vertex `n`.
24. **A state that misses part of the situation** (keys held, stops used, direction faced): BFS then merges states that are different and returns a wrong answer.

## 21. Summary

- A **graph** is vertices plus edges: directed or undirected, weighted or not. Costs are written with `V` and `E`. Trees are connected graphs without cycles.
- **Store** it as an adjacency list (default, `O(V + E)` memory), an adjacency matrix (`O(V²)`, `O(1)` edge test, dense graphs and Floyd-Warshall) or an edge list (input, Kruskal, Bellman-Ford). Grids and puzzles are **implicit graphs**: write a neighbour function instead of building edges.
- **BFS** (queue, mark on push) visits by distance and gives **fewest-edge** paths, with `parent` links for the path itself. Multi-source BFS starts with all sources in the queue. `O(V + E)`.
- **DFS** (recursion or a stack) goes deep first and knows when a vertex is **finished**. Recursive DFS hits the recursion limit near depth 1,000; the iterator-stack version does not. `O(V + E)`.
- **Components:** start a search from every unvisited vertex. **Union-Find** (union by size + path compression, `≈ O(1)` per operation) handles groups that merge over time and undirected cycle detection.
- **Cycles:** undirected → a visited neighbour other than the edge we came by; directed → an edge to a **grey** vertex (on the current path), or Kahn's order shorter than `V`.
- **Topological sort** (DAGs only): Kahn's in-degree queue, or reversed DFS finishing order. A heap gives the smallest order; rounds give "semesters". DP on a DAG (longest path, counting paths) runs in topological order.
- **Bipartite** = no odd cycle; check by 2-colouring every component.
- **Shortest paths:** BFS (unweighted), 0-1 BFS (deque), Dijkstra (heap, non-negative weights, `O((V + E) log V)`), Bellman-Ford (negative edges, detects negative cycles, `O(V · E)`), Floyd-Warshall (all pairs, `O(V³)`, `k` outermost).
- **MST:** cut property; Kruskal (sort + DSU, `O(E log E)`), Prim (heap, `O(E log V)`; array `O(V²)` for dense graphs). An MST is not a shortest-path tree.
- **SCCs:** Kosaraju (finish order, then DFS on the reversed graph) or Tarjan (one DFS with `index`/`low` and a stack). The condensation is a DAG.
- **Bridges / articulation points:** one DFS with `tin` and `low`. Bridge: `low[v] > tin[u]`. Articulation point: `low[v] >= tin[u]` for a child (root: two or more children). Skip the arriving **edge**, not the parent vertex.

### Self-check

- [ ] I can build an adjacency list from an edge list (directed, undirected, weighted, 1-based) without losing isolated vertices.
- [ ] I can write BFS with distances and parents from memory, and explain why it gives the fewest edges.
- [ ] I can write DFS recursively and with a stack, and explain the recursion-limit trap.
- [ ] I can count components on a graph and on a grid, and use multi-source BFS.
- [ ] I can detect a cycle in an undirected and in a directed graph, and explain why the methods differ.
- [ ] I can write Kahn's algorithm and the DFS topological sort, and use the order for DP.
- [ ] I can check bipartiteness and explain the odd-cycle rule.
- [ ] I can write Union-Find with both optimisations and say what each one buys.
- [ ] I can write Dijkstra with a heap and lazy deletion, and show why negative edges break it.
- [ ] I can use 0-1 BFS, Bellman-Ford (with negative-cycle detection and the copy for `k` limits), and Floyd-Warshall.
- [ ] I can choose a shortest-path algorithm from the edge weights.
- [ ] I can build an MST with Kruskal and with Prim.
- [ ] I can find SCCs with Kosaraju or Tarjan, and bridges and articulation points with low-links.
- [ ] Given a word problem, I can say what the vertices, edges and the right algorithm are.

### How to practise

Work through the problems in the order of the chapter: representations and BFS/DFS first, then components and grids, then cycles, topological sort and bipartite checks, then Union-Find, then the shortest-path family, then MSTs, and last SCCs and bridges. **Before writing code, say aloud what a vertex is, what an edge is, and whether the graph is directed and weighted.** Draw the small examples by hand and trace the queue, the stack or the heap. Test each solution against a brute force on small random graphs (as we did for bridges): include an empty graph, a single vertex, a disconnected graph, self-loops and parallel edges, and a long chain for the recursion limit. The site problems for this module (LeetCode, CSES, Codeforces) will be listed for you in the module's external list; the CSES "Graph Algorithms" section is an excellent sequence.

### Further reading

- Thomas Cormen, Charles Leiserson, Ronald Rivest and Clifford Stein, *Introduction to Algorithms*, Part VI ("Graph Algorithms"): elementary graph algorithms, MSTs, single-source and all-pairs shortest paths.
- Robert Sedgewick and Kevin Wayne, *Algorithms*, chapter 4 ("Graphs"), with clear pictures of BFS, DFS, Kosaraju, Prim, Kruskal, Dijkstra and Bellman-Ford.
- Steven Skiena, *The Algorithm Design Manual*, chapters 7 and 8, especially the "war stories" on modelling problems as graphs.
- Antti Laaksonen, *Competitive Programmer's Handbook* (free online), chapters 11 to 17, the companion to the CSES problem set.
- Robert Tarjan, "Depth-First Search and Linear Graph Algorithms" (1972), the paper that introduced low-link values for SCCs and biconnectivity.
- Edsger Dijkstra, "A Note on Two Problems in Connexion with Graphs" (1959), two pages that give both the shortest-path algorithm and an MST algorithm.

Next module: **dsa.13 Greedy algorithms**.
