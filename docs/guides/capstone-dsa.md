# DSA capstone: your own algorithms library

You have finished (or nearly finished) the DSA track. The capstone proves you can turn
what you learned into a **small, tested, measured library** that you could hand to
someone else. You choose the structure, write the code, prove it correct and measure it.
Nobody gives you a solution. The checklist at the bottom is how you (or a reviewer)
decide it is done.

Syllabus line: *Your own algorithms library with tests and benchmarks.*

## Rules

- **It is yours.** Your design, your code. Use the course chapters, your own solutions
  and the official docs, not generated code. A reviewer (a friend, or Claude in tutor mode)
  reads and comments; they do not rewrite it.
- **Own folder, own repo.** Keep it outside `my-work/`, with its own git history on your
  personal GitHub. Never a company account or company remote.
- **Standard library only** for the library itself (`pytest` for tests is fine). A DSA
  library that imports `networkx` or `sortedcontainers` proves nothing. Anything you do
  install must be listed in `pyproject.toml`.
- **Size.** About 1,200-3,000 lines of library code, plus tests. Smaller than that and it
  is a snippet collection; much bigger and you will never finish.
- **Time-box.** Plan 2-4 weeks of part-time work. Write the design note first (below).

## What to build

A package, for example `algolib`, with **at least 10 items** spread over **at least 4
areas** of the track. Pick what you enjoyed or struggled with; struggling items teach most.

| Area | Items you can choose from |
|---|---|
| Searching and sorting | binary search family (`bisect` left/right, on answer), merge sort, quick-select, counting sort |
| Linear structures | stack with `min()` in O(1), monotonic stack helpers, queue from two stacks, linked list, LRU cache |
| Hashing and strings | frequency helpers, trie, KMP, Z-function, Rabin-Karp, Manacher |
| Trees and heaps | BST with iterators, heap from scratch, indexed priority queue, segment tree, Fenwick tree |
| Graphs | BFS, DFS, topological sort, Union-Find, Dijkstra, Kruskal, SCC, bridges |
| Dynamic programming | LIS, LCS, edit distance, knapsack with reconstruction, bitmask DP |
| Greedy and recursion | interval scheduling, Huffman, permutations, subsets, N-Queens |

Rules for the choice:

1. At least **3 data structures** (classes) and at least **5 algorithms** (functions).
2. At least **2 items that exist in two versions** (for example, recursive and iterative
   DFS, or `O(n^2)` and `O(n log n)` LIS), so benchmarks have something to compare.
3. One item must be something the standard library does **not** give you.

If you cannot decide in a day, take this default: stack with `min`, binary heap, Union-Find,
trie, Dijkstra, LIS (two versions), LCS with reconstruction, merge sort, Fenwick tree,
topological sort.

## Step 0: the design note (1 page, before any code)

Write `DESIGN.md` and keep it in the repo:

1. One-sentence purpose and who would use it.
2. The public API: every function and class with its signature and one example call.
3. For each item: input limits, time and space complexity, and the invariant you will test.
4. The layout: which module owns which area, and what is shared (for example, a common
   `Graph` type).
5. Error policy: what happens on bad input (an exception from your own small hierarchy, or
   a documented return value) and what is **not** checked.
6. The benchmark plan: which items you will compare, and on which input sizes.
7. What you are deliberately *not* building.

Bring `DESIGN.md` to the reviewer before you write much code.

## Requirements

Tick every **Must**. Aim for most **Should** items. **Stretch** is optional.

### A. Correctness

- **Must:** every item has unit tests with normal cases and at least 3 edge cases (empty
  input, one element, duplicates, already sorted, all equal, maximum size).
- **Must:** every algorithm is compared against a **brute-force** version on at least
  200 random small inputs (a stress test with a fixed random seed).
- **Must:** every data structure has a test for its invariant after many random operations
  (heap property, Union-Find component count, Fenwick prefix sums, and so on).
- **Should:** parametrised tests for input validation; `hypothesis` for at least one item.
- **Should:** negative tests: a negative edge for Dijkstra, a cycle given to topological
  sort, an empty heap `pop`. Each gives the documented error, not a traceback from inside.
- **Stretch:** break one algorithm on purpose and confirm a test fails (a mutation check).

### B. Performance and benchmarks

- **Must:** a `benchmarks/` script using `time.perf_counter`, taking the **best of
  several runs**, that prints a table: item, input size, time.
- **Must:** a **doubling test** for at least 4 items: run at sizes `n, 2n, 4n, 8n` and
  show the time ratio. A ratio near 2 means `O(n)`, near 4 means `O(n^2)`, and so on.
- **Must:** at least 2 comparisons of two versions of the same item (for example, your
  heap against `heapq`, or `O(n^2)` against `O(n log n)` LIS), with a one-paragraph
  explanation of the result in the README.
- **Should:** a benchmark of your structure against the Python built-in that does the
  same job, with an honest note when the built-in wins (it often does, because it is C).
- **Should:** worst-case inputs, not only random ones (sorted input for quicksort, a long
  chain for DFS recursion depth).
- **Stretch:** a small plot or ASCII chart of time against `n`.

### C. Code quality

- **Must:** a package layout (`src/algolib/` with `__init__.py`), not one big file.
- **Must:** type hints on every public function; the checker (`mypy`) is clean, or each
  ignore has a comment.
- **Must:** a docstring on every public item with: what it does, parameters, return value,
  **time and space complexity**, and one example.
- **Must:** no recursion that can hit the default limit on valid input. Either use an
  iterative version or document the limit.
- **Should:** generics where they fit (`TypeVar`) so structures hold more than `int`.
- **Should:** `__len__`, `__iter__`, `__repr__` on the structures, as a Python user expects.
- **Should:** `ruff` (or flake8) and a formatter are clean.
- **Stretch:** a `Protocol` for "something with `push` and `pop`" used by two structures.

### D. Packaging

- **Must:** `pyproject.toml` with name, version, Python requirement and dependencies, so
  `pip install -e .` works.
- **Must:** it installs and the tests run in a **fresh** virtual environment (try it).
- **Should:** version stored in one place; a `CHANGELOG.md` with at least one entry.
- **Stretch:** build a wheel and install it in another venv.

### E. Documentation

- **Must:** `README.md` with: what it is, install steps, a quick start with one example
  per area, and a **complexity table** for every item.
- **Must:** a "Benchmarks" section with the tables from part B and what they show.
- **Must:** `DESIGN.md` updated to match what you actually built.
- **Should:** a "Known limits" section: honest list of what it does not do.
- **Stretch:** a short "when to use which" guide for your own items.

### F. Engineering habits

- **Must:** git history with many small commits with clear messages (one item per commit
  is a good rhythm).
- **Must:** no secrets, no personal data, no machine paths in the repo.
- **Should:** a `.gitignore`; benchmark output files kept out of git.
- **Stretch:** a small CI file that runs the tests (even if you never push it).

## How the review works

1. **Design review** (before coding): the reviewer reads `DESIGN.md` and asks questions.
   Typical outcomes: "too big, cut X" or "what is the invariant of Y?".
2. **Midpoint check:** about half the items done with tests and stress tests. The reviewer
   runs them and tries to break them with their own inputs.
3. **Final review:** run through the checklist above. For every unticked **Must** the
   reviewer gives a pointer, not a patch ("what does your `pop` do on an empty heap?").
4. **Fresh-machine test:** clone the repo into a new folder, create a new venv, follow
   only the README. If you get stuck, the README is the bug.

### Scoring (for yourself)

| Score | Meaning |
|---|---|
| All Musts, most Shoulds | DSA capstone passed |
| All Musts only | Passed, but go back and add tests and documentation polish |
| Any Must missing | Not done yet. Finish those first |

Stretch items are for pride and for your portfolio, not for the pass mark.

## Why this capstone

Anyone can read an algorithm. Writing it, breaking it with random tests and watching its
real running time follow the curve you predicted is what turns a DSA course into a skill.
The brute-force stress test and the doubling benchmark are the two habits to keep for life.
