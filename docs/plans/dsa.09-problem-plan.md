# Problem plan: dsa.09 Linked lists (35 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.09.p001`…`p035`.
**Mix:** 12 drill, 12 applied, 7 deep, 4 challenge. Kinds: 32 code, 2 trace, 1 explain. **assessment:** explain = p006, trace = p011, fix = p018, build = p035.
Shared test helper (in every `test_solution.py`): `build(values)` makes a list, `to_list(head)` walks it with a step limit (10**5) so a cycle becomes a failure message "your list has a cycle". Tests also check **nothing lost, nothing duplicated**: node identities are collected before and after.

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Build and print a list | drill | code | `from_list`, `to_list`; empty list is `None` |
| 2 | Length and k-th node | drill | code | `length(head)`, `get(head, k)`; k out of range returns `None` |
| 3 | Append at the tail | drill | code | O(n) walk; empty list; node identity kept |
| 4 | Find a value | drill | code | return index or -1; first of duplicates |
| 5 | Variables are labels | drill | trace | `⚠ HAND-TRACE` which of 6 names point to which node after a rewiring snippet; expected as list of values |
| 6 | Why does order matter when rewiring? | drill | explain | explain what is lost if `nxt` is not saved first; graded by terms ("lost", "save", "next") |
| 7 | Singly linked list class | applied | code | `push_front/push_back/pop_front/remove/__len__/__iter__`; random operations vs list model (fixed seed) |
| 8 | Remove all nodes with a value | drill | code | dummy node; head removals, all removed, none removed |
| 9 | Insert into a sorted list | drill | code | dummy node; front, middle, end, duplicates |
| 10 | Doubly linked list with sentinels | applied | code | `append/appendleft/pop/popleft/remove_node`; random ops vs deque; prev/next consistency check |
| 11 | Trace the three-variable reversal | drill | trace | `⚠ HAND-TRACE` `prev`, `cur`, `nxt` after each iteration for `1→2→3→4` |
| 12 | Reverse a list (iterative) | drill | code | empty, 1 node, 2 nodes; node identities reused |
| 13 | Reverse a list (recursive) | applied | code | 1000 nodes works under the recursion limit; message when deeper fails |
| 14 | Reverse between positions | applied | code | `left..right` inclusive; left=1; right=n |
| 15 | Reverse in groups of k | challenge | code | tail group shorter than k stays; k=1; brute-force compare |
| 16 | Middle of the list | drill | code | even length → second middle; fast/slow; step counter check |
| 17 | Detect a cycle | applied | code | Floyd; no extra set (test counts memory via node attributes: forbids marking nodes) |
| 18 | Fix the broken cycle detector | applied | code | `assessment = "fix"`; given a version that loops forever on a 2-node cycle |
| 19 | Start of the cycle | deep | code | return the node; no cycle → `None`; `⚠ HAND-TRACE` tail length 3, cycle length 4 |
| 20 | Length of the cycle | applied | code | after meeting, walk once round |
| 21 | Happy number | applied | code | fast/slow on numbers; 19 true, 2 false |
| 22 | Find the duplicate number | deep | code | array treated as list, no modification, O(1) space; `[1,3,4,2,2]` |
| 23 | Merge two sorted lists | drill | code | stable; one empty; reuse nodes |
| 24 | Merge k sorted lists | deep | code | heap or divide and conquer; `heapq` tie handling with a counter |
| 25 | Sort a linked list | deep | code | merge sort O(n log n); 10**4 nodes in time; stable |
| 26 | Remove the n-th node from the end | applied | code | one pass; n = length removes head |
| 27 | Palindrome list in O(1) space | deep | code | reverse the second half; list is restored afterwards (test checks) |
| 28 | Reorder list | deep | code | `1→2→3→4→5` → `1→5→2→4→3`; in place |
| 29 | Rotate right by k | applied | code | k larger than length; k=0 |
| 30 | Partition around a value | applied | code | stable within each side; two dummies |
| 31 | Add two numbers stored as lists | applied | code | reversed digits; carry at the end; different lengths |
| 32 | Intersection of two lists | challenge | code | node identity, not value; lists of different length; O(1) space |
| 33 | Copy a list with random pointers | challenge | code | deep copy: no shared nodes; random pointers preserved; interleaving method |
| 34 | LRU cache | challenge | code | `get/put` O(1) with dict + doubly linked list; compare with `OrderedDict` model on random ops; `⚠ HAND-TRACE` one scripted sequence of evictions |
| 35 | Build your own stack and queue on nodes | deep | code | `assessment = "build"`; `LinkedStack` and `LinkedQueue` with O(1) ends; ops vs deque model |

## Counts
Trace: 5, 11, 19, 34 are hand-traced; to reach 8 turn p9, p26 and p30 into trace questions ("write the list after each step"), plus p13 (recursion unwinding). Explain: 6 plus p17 (why two pointers meet), p21 (why a happy-number loop is a cycle), p27 (why restore the list), p13 (why recursion limit) as short written variants if exactly 5 is wanted. Keep one `assessment` of each kind.

## Real-site problems (`external.toml`)
LeetCode `reverse-linked-list`, `reverse-linked-list-ii`, `reverse-nodes-in-k-group`, `middle-of-the-linked-list`, `linked-list-cycle`, `linked-list-cycle-ii`, `merge-two-sorted-lists`, `merge-k-sorted-lists`, `sort-list`, `remove-nth-node-from-end-of-list`, `palindrome-linked-list`, `reorder-list`, `rotate-list`, `partition-list`, `add-two-numbers`, `intersection-of-two-linked-lists`, `copy-list-with-random-pointer`, `lru-cache`, `find-the-duplicate-number`, `happy-number`, `odd-even-linked-list`, `remove-duplicates-from-sorted-list`. Ids unverified.
