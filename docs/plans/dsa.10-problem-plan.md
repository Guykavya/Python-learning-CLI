# Problem plan: dsa.10 Trees (60 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.10.p001`…`p060`. Use ONE shared helper per `test_solution.py`: `build(level_order_list)` (None for gaps) and `to_level(root)`. Starter code defines `class TreeNode` (`val`, `left`, `right`).
**Mix:** 19 drill, 26 applied, 11 deep, 4 challenge. Kinds: 51 code (incl. fix p033 and build p060), 6 trace, 3 explain. **assessment:** explain = p007, trace = p016, fix = p033, build = p060.
Deep trees: tests that build a 5,000-node chain must not use a recursive builder; solutions using recursion on such input get the message "use an iterative version or raise the limit knowingly". Compare against brute force / `sorted()` on random trees (fixed seed).

## A. Shape and recursion (Ch. 1–3)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | Size of a tree | drill | code | empty → 0 |
| 2 | Sum of all values | drill | code | negative values |
| 3 | Maximum value | drill | code | empty returns `None` with message |
| 4 | Count leaves | drill | code | single node is a leaf |
| 5 | Height of a tree | drill | code | empty = 0 (state the convention in the statement) |
| 6 | Mirror (invert) a tree | drill | code | returns the same node objects; compare shapes |
| 7 | What does each call return? | drill | explain | for `size`, `height`, `is_leaf`, say what a call returns for `None`; graded by terms |
| 8 | Count nodes with one child | applied | code | |
| 9 | Values at depth d | applied | code | `d` beyond height → `[]` |
| 10 | Draw a tree from a description | drill | trace | `⚠ HAND-TRACE` level-order list given, expected: height, leaves, size |

## B. Traversals (Ch. 4–6)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 11 | Preorder, inorder, postorder (recursive) | drill | code | three functions |
| 12 | Preorder (iterative) | applied | code | explicit stack; 5,000-node chain works |
| 13 | Inorder (iterative) | applied | code | |
| 14 | Postorder (iterative) | deep | code | one or two stacks |
| 15 | Traversal generator | applied | code | lazy `iter_inorder`; take first 3 from a huge tree |
| 16 | Trace the iterative inorder | drill | trace | `⚠ HAND-TRACE` stack contents after each step on a 6-node tree |
| 17 | Level order | drill | code | list of levels; empty tree → `[]` |
| 18 | Zigzag level order | applied | code | alternate direction |
| 19 | Right side view | applied | code | |
| 20 | Good nodes | applied | code | preorder that carries the maximum so far down; a node is good if no ancestor is larger; negatives, single node, chain |
| 21 | Trace the queue in a level-order walk | drill | trace | `⚠ HAND-TRACE` print the queue contents after each pop on a 6-node tree; expected lines come from running the code |
| 22 | Expression tree evaluation | applied | code | postorder; `+ - * /` |
| 23 | Which traversal gives this? | drill | trace | `⚠ HAND-TRACE` given a tree, write all three orders; answers as lists |
| 24 | Morris traversal (no stack, no recursion) | challenge | code | O(1) extra space: test checks the tree is restored. The chapter only names Morris (sec. 5) and does not teach it: the statement describes the thread idea and the hints walk through it |

## C. Height, balance, diameter, paths (Ch. 7–8)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 25 | Minimum depth | applied | code | trap: a node with one child is not a leaf; skewed tree test |
| 26 | Balanced tree? | applied | code | O(n): test with a counter that forbids recomputing heights |
| 27 | Diameter | applied | code | edges convention in the statement; path not through the root |
| 28 | Has a root-to-leaf path with sum | drill | code | |
| 29 | All root-to-leaf paths | applied | code | strings or lists; backtracking un-choose |
| 30 | Sum of root-to-leaf numbers | applied | code | digits formed along the path |
| 31 | Path sum III (any downward path) | deep | code | prefix-sum dictionary; negatives |
| 32 | Maximum path sum | challenge | code | negative nodes; single node |
| 33 | Fix the diameter | applied | code | `assessment = "fix"`; given code that counts only paths through the root |
| 34 | Longest univalue path | deep | code | |

## D. Binary search trees (Ch. 9)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 35 | BST search, min, max | drill | code | |
| 36 | BST insert | drill | code | duplicates ignored; compare with a sorted set |
| 37 | BST delete | deep | code | leaf, one child, two children; compare with a set after random operations |
| 38 | Validate a BST | applied | code | trap: a node that is fine against its parent but not an ancestor; values at int limits |
| 39 | Trace a BST delete | applied | trace | `⚠ HAND-TRACE` the tree (level order) after deleting 3 given keys |
| 40 | Shape depends on insertion order | drill | explain | graded by terms ("sorted", "chain", "height n") |
| 41 | K-th smallest | applied | code | inorder with early stop |
| 42 | Inorder successor | applied | code | no parent pointer; last node → `None` |
| 43 | Floor and ceiling | applied | code | |
| 44 | Range sum in a BST | applied | code | pruning: counter limits nodes visited |
| 45 | BST iterator | deep | code | `next/has_next` with O(h) memory |
| 46 | Recover a BST with two swapped nodes | challenge | code | swap the two VALUES back (nodes stay in place); not in the chapter, so the hints teach it: in the inorder list look for the descents (one or two); adjacent and far-apart swaps |

## E. LCA, construction, serialisation (Ch. 10–11)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 47 | LCA in a binary tree | applied | code | node is its own ancestor; brute force on parent paths |
| 48 | LCA in a BST | drill | code | uses the order, no full search (counter) |
| 49 | Distance between two nodes | deep | code | |
| 50 | Build from preorder + inorder | deep | code | check by re-traversing; distinct values |
| 51 | Build from postorder + inorder | deep | code | |
| 52 | Serialise and deserialise | deep | code | round trip on random trees including `None` gaps |
| 53 | Sorted array to balanced BST | applied | code | heights differ by at most 1 |
| 54 | Why one traversal is not enough | applied | explain | give two different trees with the same preorder, as level-order lists, and say what extra information fixes it; self-rated against `answer.md` (explain problems are never machine-graded) |

## F. Comparing, reshaping, representations, balancing (Ch. 12–14)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 55 | Same tree? / symmetric? | drill | code | two functions |
| 56 | Subtree of another tree | applied | code | |
| 57 | Flatten to a linked list | deep | code | in place, preorder; right pointers only |
| 58 | Parent array to children lists and depths | applied | code | Ch. 13: `parent[i]`, root has -1; return `(children, depth)`; a parent that comes AFTER its child in the array; a single node; a path of 5,000 nodes (no recursion) |
| 59 | Trace an AVL insertion | challenge | trace | `⚠ HAND-TRACE` rotations and final level order when inserting `10,20,30,40,50,25` |
| 60 | Build a BST class with tests | deep | code | `assessment = "build"`; `insert/delete/contains/height/inorder/__len__`; sorted insertion of 2,000 keys must not recurse past the limit; checks against `set` |

## Counts
Tiers 19 drill / 26 applied / 11 deep / 4 challenge. Traces: p010, p016, p021, p023, p039, p059 (6). Explain: p007, p040, p054 (3). Fix: p033. Build: p060. Everything else is code (51). Changes against the first draft of this plan (made 2026-11-16): the old count line said 20/20/14/6, which did not match the table; p020 Level averages (trivial) became Good nodes; p021 Bottom-up level order (trivial) became a queue trace; p058 Good nodes moved to p020 and p058 now covers Ch. 13 (the parent array), the only chapter section without a problem; p054 was marked "graded by checking" but explain problems are self-rated.

## Real-site problems (`external.toml`)
LeetCode `maximum-depth-of-binary-tree`, `invert-binary-tree`, `binary-tree-inorder-traversal`, `binary-tree-level-order-traversal`, `binary-tree-zigzag-level-order-traversal`, `binary-tree-right-side-view`, `balanced-binary-tree`, `diameter-of-binary-tree`, `path-sum`, `path-sum-iii`, `binary-tree-maximum-path-sum`, `validate-binary-search-tree`, `kth-smallest-element-in-a-bst`, `delete-node-in-a-bst`, `lowest-common-ancestor-of-a-binary-tree`, `lowest-common-ancestor-of-a-binary-search-tree`, `construct-binary-tree-from-preorder-and-inorder-traversal`, `serialize-and-deserialize-binary-tree`, `convert-sorted-array-to-binary-search-tree`, `subtree-of-another-tree`, `flatten-binary-tree-to-linked-list`, `count-good-nodes-in-binary-tree`, `recover-binary-search-tree`; CSES 1131 Tree Diameter (needs an iterative walk: 2*10^5 nodes). CSES 1130 Tree Matching is left out (needs a greedy idea this module does not teach). Slugs are written from memory and unverified: say so in `external.toml`, as dsa.09 does.
