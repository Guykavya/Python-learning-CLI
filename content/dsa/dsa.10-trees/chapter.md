# dsa.10 Trees

## 1. Data that branches

A list is a line: every item has one next item. But a lot of real data is not a line. It **branches**.

- A folder holds files and more folders, which hold more files and folders.
- A web page is a `<html>` element that holds `<head>` and `<body>`, which hold more elements.
- A family tree, a company chart, a tournament bracket, the parts of a car.
- The expression `(3 + 4) * 2` has a `*` at the top with two parts below it.
- A decision: "Is it raining? If yes, take an umbrella. If no, is it sunny? ..."

All of these are **trees**. A tree has one starting point at the top, the **root**. Every item can have items below it (its **children**). Every item except the root has exactly one item above it (its **parent**). There are no loops: if you start from any item and keep going up, you reach the root, and you never meet the same item twice.

In a **binary tree**, every item has **at most two** children, called the **left** child and the **right** child. Almost everything in this module is about binary trees, because two children are enough to build every important structure (search trees, heaps, expression trees), and the ideas carry over to trees with more children.

### The words you must know

```text
                 4             <- root (no parent), depth 0
               /   \
              2     6          <- 2 and 6 are siblings; children of 4; depth 1
             / \   / \
            1   3 5   7        <- leaves (no children), depth 2
```

| Word | Meaning |
|---|---|
| **root** | the top node; the only one without a parent |
| **parent / child / sibling** | the node above / the nodes below / the nodes with the same parent |
| **leaf** | a node with no children (4 is not a leaf; 1, 3, 5, 7 are) |
| **subtree** | a node together with everything below it. Every node is the root of its own subtree |
| **depth** of a node | how many steps it is from the root (the root has depth 0) |
| **height** of a node | the length of the longest downward path from it to a leaf |
| **height of the tree** | the height of the root |
| **level** | all nodes with the same depth |
| **ancestor / descendant** | any node on the way up to the root / any node below |

A subtle point: **"height" is counted in two ways.** Many textbooks count *edges* (the arrows between nodes), so a single node has height 0 and an empty tree has height -1. Many coding problems count *nodes* on the path, so a single node has height 1 and an empty tree has height 0. This chapter counts **nodes** (the second way, because it makes the code simpler: `height(None) = 0`). Whenever a problem says "depth" or "height", check which way it counts.

### What you can do after this module

1. **Solve tree problems by defining what each recursive call returns**, the one idea that makes most of them short.
2. **Traverse a tree** in preorder, inorder, postorder and level order, both recursively and with an explicit stack or queue.
3. **Compute height, diameter, balance and path sums**, and find the **lowest common ancestor**.
4. **Use a binary search tree**: search, insert, delete, validate, and find the k-th smallest.
5. **Build a tree from traversals** and **serialise** it to text and back.
6. **Explain why balance matters**, and read the idea behind AVL and red-black trees.

### A first look

A tree is built from nodes, like a linked list, but each node has two links instead of one.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

root = TreeNode(4, TreeNode(2), TreeNode(6))
print(root.val, root.left.val, root.right.val, root.left.left)
```
```text
4 2 6 None
```

`root.left.left` is `None`: the node `2` has no left child. As with linked lists, `None` means "nothing here", and a very common error is calling `.val` or `.left` on `None`.

## 2. Building and printing trees

Typing nested `TreeNode(...)` calls is slow and hard to read. We need three helpers. They are used in every example of this chapter (copy them to the top of your own file); the code blocks below do not repeat them.

1. `build_tree(values)` builds a tree from a list in **level order**, where `None` means "no node here". This is the format that many problem sites use: `[3, 9, 20, None, None, 15, 7]`.
2. `to_level_list(root)` goes the other way.
3. `show_tree(root)` prints a tree sideways, so you can see its shape in the terminal.

```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build_tree(values):
    """Level-order list -> tree. None means a missing node."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root

def to_level_list(root):
    """Tree -> level-order list with None for gaps (trailing Nones removed)."""
    if root is None:
        return []
    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
        else:
            out.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out

def show_tree(root):
    """The tree turned 90 degrees: the right subtree is on top, the left one at the bottom."""
    lines = []
    def go(node, depth):
        if node is None:
            return
        go(node.right, depth + 1)
        lines.append("    " * depth + str(node.val))
        go(node.left, depth + 1)
    go(root, 0)
    return "\n".join(lines) if lines else "(empty)"

bst = build_tree([4, 2, 6, 1, 3, 5, 7])
print(show_tree(bst))
print(to_level_list(bst))
```
```text
        7
    6
        5
4
        3
    2
        1
[4, 2, 6, 1, 3, 5, 7]
```

Tilt your head to the left to read the picture: the root `4` is at the left edge, `6` and `2` are its children (right on top, left on the bottom), and the leaves are the deepest, indented columns.

How does `build_tree` read `[3, 9, 20, None, None, 15, 7]`? It takes values two at a time as the left and right child of the nodes in a queue, in the order the nodes appear. The root is `3`. Its children are `9` and `20`. Then the children of `9` are `None, None` (a leaf), and the children of `20` are `15` and `7`. The queue (dsa.08) is what keeps the order straight.

```python
example = build_tree([3, 9, 20, None, None, 15, 7])
print(show_tree(example))
print(to_level_list(example))
print(to_level_list(build_tree([1, None, 2, 3])))
```
```text
        7
    20
        15
3
    9
[3, 9, 20, None, None, 15, 7]
[1, None, 2, 3]
```

We use two trees often. `bst` (above) is a *search tree* with the numbers 1 to 7. `example` is a general tree that is not ordered and not balanced.

### Tree shapes

The shape decides the speed of almost everything. With `n` nodes and height `h` (counting nodes):

| Shape | What it looks like | Height |
|---|---|---|
| **Perfect** | every level is completely full | `n = 2^h - 1`, so `h = log2(n + 1)` |
| **Complete** | every level full except possibly the last, which is filled from the left | `h = ceil(log2(n + 1))` (heaps use this shape) |
| **Balanced** | the two sides of every node differ in height by at most 1 | about `log2 n` |
| **Skewed (degenerate)** | every node has one child: it is a linked list | `h = n` |

The same `n` nodes can give a height of about 20 (for a million nodes) or a height of a million. A perfect tree has about **half of its nodes in the last level**, so most nodes are deep; the height grows only as `log n`. Remember this table: when we say "`O(h)`" later, `h` is between `log n` and `n`, and the whole question of tree design is how to keep `h` near `log n`.

```python
import math

for n in (7, 1000, 1_000_000):
    print(f"n={n:>9}: perfect/balanced height about {math.ceil(math.log2(n + 1)):>2}, skewed height {n}")
```
```text
n=        7: perfect/balanced height about  3, skewed height 7
n=     1000: perfect/balanced height about 10, skewed height 1000
n=  1000000: perfect/balanced height about 20, skewed height 1000000
```

## 3. Thinking recursively: what does each call return?

A tree is a **recursive structure**: the left child is the root of a smaller tree, and so is the right child. A tree is either empty (`None`) or a root with a left tree and a right tree. So trees and recursion fit each other perfectly, and **most tree problems are solved with a short recursive function.** The question is how to design it.

### The one question

Before you write any code, finish this sentence:

> **"`f(node)` returns ________ for the tree that starts at `node`."**

Then answer two small questions:

1. **What does `f(None)` return?** (the base case: an empty tree)
2. **If I already have `f(node.left)` and `f(node.right)`, how do I get `f(node)`?** (trust the recursive calls; combine them with `node.val`)

That is the whole method. It is the "trust the recursion" idea of dsa.07, and here it is easy because the subproblems (left and right subtrees) are obvious and do not overlap.

### Example: the size of a tree

> `size(node)` returns the number of nodes in the tree that starts at `node`.

- `size(None) = 0`
- `size(node) = 1 + size(left) + size(right)`

```python
def size(node):
    if node is None:
        return 0
    return 1 + size(node.left) + size(node.right)

print(size(bst), size(example), size(None))
```
```text
7 5 0
```

### More examples with the same shape

Each function below is the same four lines with different words.

```python
def height(node):
    """Number of nodes on the longest path from `node` down to a leaf (0 for an empty tree)."""
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))

def total(node):
    """Sum of all values in the tree."""
    if node is None:
        return 0
    return node.val + total(node.left) + total(node.right)

def count_leaves(node):
    """Number of leaves (nodes without children)."""
    if node is None:
        return 0
    if node.left is None and node.right is None:
        return 1
    return count_leaves(node.left) + count_leaves(node.right)

def invert(node):
    """Swap left and right everywhere; return the root."""
    if node is None:
        return None
    node.left, node.right = invert(node.right), invert(node.left)
    return node

for tree in (bst, example):
    print(size(tree), height(tree), total(tree), count_leaves(tree))
print(to_level_list(invert(build_tree([4, 2, 6, 1, 3, 5, 7]))))
```
```text
7 3 28 4
5 3 54 3
[4, 6, 2, 7, 5, 3, 1]
```

Look at `count_leaves`: there are **two** base cases. `None` returns 0 (nothing there), but a leaf returns 1 (one leaf). If you wrote only the `None` case, the function would return 0 for every tree, because the recursion ends only in `None`. A common slip.

Look at `invert`: it returns the node itself, and the assignment `node.left, node.right = invert(node.right), invert(node.left)` evaluates both calls first, then swaps. Its contract is "returns the root of the inverted tree".

### The recursion tree is the tree

Draw the calls of `size(bst)`: `size(4)` calls `size(2)` and `size(6)`, which call `size(1)`, `size(3)`, `size(5)`, `size(7)`, and each of these calls `size(None)` twice. The tree of calls is the tree itself, plus a `None` below each missing child. A tree with `n` nodes has `n + 1` missing children, so there are exactly `n + (n + 1) = 2n + 1` calls. The work per call is constant, so every function above costs **`O(n)`**: each node is visited once.

```python
calls = 0

def size_counted(node):
    global calls
    calls += 1
    if node is None:
        return 0
    return 1 + size_counted(node.left) + size_counted(node.right)

for tree in (bst, example):
    calls = 0
    n = size_counted(tree)
    print("nodes:", n, "calls:", calls, "2n+1 =", 2 * n + 1)
```
```text
nodes: 7 calls: 15 2n+1 = 15
nodes: 5 calls: 11 2n+1 = 11
```

The recursion depth equals the **height** of the tree. For a balanced tree that is about `log n` (no problem). For a skewed tree with 5,000 nodes it is 5,000, which exceeds Python's recursion limit (usually 1000); see section 16.

### Two directions of information

A function can send information **up** (through its return value) or **down** (through its parameters).

- **Up (bottom-up):** the answer for a node is built from the answers of its children. `size`, `height`, `total` work this way. Use this when the question is about a whole subtree.
- **Down (top-down):** the node receives something from above: its depth, the path so far, the allowed range. Use this when what you do at a node depends on the way you came.

Here is a top-down example: print every node with its depth. The parameter `depth` grows by 1 on the way down.

```python
def print_depths(node, depth=0):
    if node is None:
        return
    print("  " * depth + f"{node.val} (depth {depth})")
    print_depths(node.left, depth + 1)
    print_depths(node.right, depth + 1)

print_depths(example)
```
```text
3 (depth 0)
  9 (depth 1)
  20 (depth 1)
    15 (depth 2)
    7 (depth 2)
```

Many harder problems mix both: information goes down as parameters, answers come up as return values. Section 8 (paths) and section 9 (validating a BST) do both.

**Predict the output 1.** What does this print?

```python
def f(node):
    if node is None:
        return 0
    return node.val + max(f(node.left), f(node.right))

print(f(example), f(build_tree([1, 2, 3, 4])), f(None))
```

<details><summary>Answer</summary>

```text
38 7 0
```

`f` returns the value of the best (largest sum) path that goes **down** from `node` to a leaf. For `example` (`3, 9, 20, 15, 7`) the best path is `3 -> 20 -> 15`, sum 38. For `[1, 2, 3, 4]` the tree is `1` with children `2` (which has the child `4`) and `3`; the best path is `1 -> 2 -> 4`, sum 7. Here the function mixes `node.val` with the *best* of the two children, not their sum, which is the difference from `total`.

</details>

**Try it 1.** Write `count_even(node)`, returning how many nodes hold an even value, and `max_value(node)`, returning the largest value (and `None` for an empty tree). Which of the two needs more care with the base case?

<details><summary>Answer</summary>

```python
def count_even(node):
    if node is None:
        return 0
    return (node.val % 2 == 0) + count_even(node.left) + count_even(node.right)

def max_value(node):
    if node is None:
        return None
    best = node.val
    for child in (node.left, node.right):
        child_best = max_value(child)
        if child_best is not None and child_best > best:
            best = child_best
    return best

print(count_even(bst), max_value(bst), max_value(example), max_value(None))
```
```text
3 7 20 None
```

`max_value` needs the care: for an empty tree there is no sensible number to return (`0` or `-1` could be wrong if the tree holds negative values), so we return `None` and must check for it. Another approach is to return `float("-inf")` for the empty tree, which loses against every real value.

</details>

## 4. Traversals: visiting every node

A **traversal** visits every node exactly once, in some order. For a list there is one natural order. For a tree there are several, depending on **when you handle the node relative to its two subtrees**.

For a node with a left subtree `L` and a right subtree `R`:

| Name | Order | Memory trick |
|---|---|---|
| **Preorder** | node, `L`, `R` | the node comes **before** its subtrees |
| **Inorder** | `L`, node, `R` | the node comes **in between** |
| **Postorder** | `L`, `R`, node | the node comes **after** its subtrees |

These three are all **depth-first**: they go all the way down one branch before they try the next. They differ only in the place of one line.

```python
def preorder(node, out):
    if node is None:
        return
    out.append(node.val)          # node first
    preorder(node.left, out)
    preorder(node.right, out)

def inorder(node, out):
    if node is None:
        return
    inorder(node.left, out)
    out.append(node.val)          # node between
    inorder(node.right, out)

def postorder(node, out):
    if node is None:
        return
    postorder(node.left, out)
    postorder(node.right, out)
    out.append(node.val)          # node last

for name, func in (("preorder", preorder), ("inorder", inorder), ("postorder", postorder)):
    out = []
    func(bst, out)
    print(f"{name:10}", out)
```
```text
preorder   [4, 2, 1, 3, 6, 5, 7]
inorder    [1, 2, 3, 4, 5, 6, 7]
postorder  [1, 3, 2, 5, 7, 6, 4]
```

### Seeing the order: walk around the tree

Imagine walking around the outside of the tree, hugging the lines, starting at the root and keeping the tree on your left. You pass each node **three times**: once on the way down to it from above, once when you come back up from its left subtree, and once when you come back up from its right subtree.

- **Preorder** records the node the **first** time you touch it.
- **Inorder** records it the **second** time (after the left subtree is done).
- **Postorder** records it the **third** time (after both subtrees are done).

This is why the three orders always contain the same nodes, only listed at different moments.

### What each order is good for

| Order | Typical use |
|---|---|
| **Preorder** | copying a tree; saving a tree to a file (the parent is listed before its children, so a reader can rebuild it); prefix notation |
| **Inorder** | on a **binary search tree** it gives the values **in sorted order**; infix notation |
| **Postorder** | anything where a node needs the results of its children first: sizes, heights, deleting a tree, evaluating an expression |

Notice that the "bottom-up" functions of section 3 (`size`, `height`) are really postorder: they combine the answers after the recursive calls.

### A generator version

The versions above fill a list passed as an argument. A generator (core.10) hands out values one at a time, which is useful when you want only the first few, or when the tree is large. `yield from` passes up the values of the recursive calls.

```python
def inorder_gen(node):
    if node is None:
        return
    yield from inorder_gen(node.left)
    yield node.val
    yield from inorder_gen(node.right)

from itertools import islice
print(list(inorder_gen(bst)))
print(list(islice(inorder_gen(bst), 3)))        # the 3 smallest values, without visiting the rest
```
```text
[1, 2, 3, 4, 5, 6, 7]
[1, 2, 3]
```

### Expression trees: where the three orders become three notations

An arithmetic expression is a tree: the leaves are numbers, and each inner node is an operator with its two operands as children. The expression `(3 + 4) * 2` is:

```text
      *
     / \
    +   2
   / \
  3   4
```

The three traversals give the three ways of writing the expression, and you met two of them in dsa.08:

```python
def evaluate(node):
    if node.left is None and node.right is None:       # a leaf: a number
        return node.val
    a, b = evaluate(node.left), evaluate(node.right)    # postorder: children first
    ops = {"+": lambda x, y: x + y, "-": lambda x, y: x - y,
           "*": lambda x, y: x * y, "/": lambda x, y: x / y}
    return ops[node.val](a, b)

def to_infix(node):
    if node.left is None and node.right is None:
        return str(node.val)
    return f"({to_infix(node.left)} {node.val} {to_infix(node.right)})"    # inorder

def to_prefix(node):
    if node.left is None and node.right is None:
        return str(node.val)
    return f"{node.val} {to_prefix(node.left)} {to_prefix(node.right)}"    # preorder

def to_postfix(node):
    if node.left is None and node.right is None:
        return str(node.val)
    return f"{to_postfix(node.left)} {to_postfix(node.right)} {node.val}"   # postorder

expr = TreeNode("*", TreeNode("+", TreeNode(3), TreeNode(4)), TreeNode(2))
print(evaluate(expr))
print(to_infix(expr))
print(to_prefix(expr))
print(to_postfix(expr))
```
```text
14
((3 + 4) * 2)
* + 3 4 2
3 4 + 2 *
```

The postfix output `3 4 + 2 *` is exactly the input of the stack evaluator from dsa.08. That evaluator is, in effect, a postorder walk of this tree made with a stack instead of recursion. The brackets in the infix version come from the tree; an inorder walk alone does not know where they belong.

**Predict the output 2.** The three traversals of the tree `[1, 2, 3, 4, 5]` (the root 1, children 2 and 3, and the children of 2 are 4 and 5). What are they?

<details><summary>Answer</summary>

```python
t = build_tree([1, 2, 3, 4, 5])
for name, func in (("preorder", preorder), ("inorder", inorder), ("postorder", postorder)):
    out = []
    func(t, out)
    print(name, out)
```
```text
preorder [1, 2, 4, 5, 3]
inorder [4, 2, 5, 1, 3]
postorder [4, 5, 2, 3, 1]
```

Preorder: `1`, then the whole left subtree (`2, 4, 5`), then `3`. Inorder: the left subtree first (`4, 2, 5`), then `1`, then `3`. Postorder: the left subtree (`4, 5, 2`), the right subtree (`3`), then the root `1` last. In every postorder the root is the **last** item; in every preorder it is the **first**. That fact is used in section 11 to rebuild a tree.

</details>

**Try it 2.** Write `leaf_values(node)` that returns the values of the leaves from left to right. Which of the three orders does it need? (Hint: any of them works for leaves. Why?)

<details><summary>Answer</summary>

```python
def leaf_values(node):
    if node is None:
        return []
    if node.left is None and node.right is None:
        return [node.val]
    return leaf_values(node.left) + leaf_values(node.right)

print(leaf_values(bst), leaf_values(example), leaf_values(None))
```
```text
[1, 3, 5, 7] [9, 15, 7] []
```

A leaf has no subtrees, so the position of "the node" relative to them does not matter: all three orders list the leaves in the same left-to-right sequence. The orders differ only for nodes that have children.

</details>

## 5. Traversals without recursion

The recursive traversals are short and clear. Why would anyone write them with a stack? Two reasons.

1. **The recursion limit.** Python allows about 1000 nested calls. A balanced tree is shallow (height about `log n`), but a **skewed** tree (nearly a linked list) with 5,000 nodes is 5,000 calls deep, and the recursive version crashes.
2. **Control.** An explicit stack lets you pause, stop early, or produce one value at a time (as in an iterator).

Here is the problem in numbers. `skewed(n)` builds a tree in which every node has only a right child.

```python
def skewed(n):
    root = None
    for v in range(n, 0, -1):
        root = TreeNode(v, None, root)
    return root

def inorder_recursive(node, out):
    if node is None:
        return
    inorder_recursive(node.left, out)
    out.append(node.val)
    inorder_recursive(node.right, out)

try:
    inorder_recursive(skewed(5000), [])
except RecursionError:
    print("recursive inorder: RecursionError on a skewed tree of 5000 nodes")
```
```text
recursive inorder: RecursionError on a skewed tree of 5000 nodes
```

### Preorder with a stack

The stack holds the nodes **still to visit**. Pop a node, visit it, then push its children. The stack gives the *last* pushed first, so to visit the left child first, push the **right child first**.

```python
def preorder_iter(root):
    out = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)             # visit
        if node.right:
            stack.append(node.right)     # pushed first, so visited last
        if node.left:
            stack.append(node.left)
    return out

print(preorder_iter(bst))
```
```text
[4, 2, 1, 3, 6, 5, 7]
```

### Inorder with a stack

Inorder is the one that needs real thought. The idea: from a node, go **as far left as you can**, remembering the path on the stack. When you cannot go left any more, pop a node (the leftmost), visit it, and then do the same on its **right** subtree.

```python
def inorder_iter(root):
    out, stack, cur = [], [], root
    while cur or stack:
        while cur:                       # go left as far as possible
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()                # the next node in sorted order
        out.append(cur.val)              # visit
        cur = cur.right                  # then handle its right subtree
    return out

print(inorder_iter(bst))
```
```text
[1, 2, 3, 4, 5, 6, 7]
```

The loop condition `while cur or stack` means: continue while there is a current node to go down from, **or** nodes waiting on the stack. Watch it on the small tree `[2, 1, 3]`:

```python
def inorder_traced(root):
    out, stack, cur = [], [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            print(f"push {cur.val}   stack={[n.val for n in stack]}")
            cur = cur.left
        cur = stack.pop()
        print(f"pop  {cur.val}   visit, stack={[n.val for n in stack]}")
        out.append(cur.val)
        cur = cur.right
    return out

print(inorder_traced(build_tree([2, 1, 3])))
```
```text
push 2   stack=[2]
push 1   stack=[2, 1]
pop  1   visit, stack=[2]
pop  2   visit, stack=[]
push 3   stack=[3]
pop  3   visit, stack=[]
[1, 2, 3]
```

At every moment the stack holds exactly the **ancestors that are still waiting for their turn** (those whose left subtree is being processed). Its size never exceeds the height of the tree.

### Postorder with a stack

Postorder is the hardest: a node is visited only after **both** subtrees are done. Two ways to do it.

**Way 1: reverse a modified preorder.** Postorder is `L, R, node`. If you do a preorder that goes *right before left* (`node, R, L`) and reverse the result, you get `L, R, node`. This is short and easy to remember.

```python
def postorder_iter(root):
    out = []
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)             # node, then right, then left ...
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return out[::-1]                      # ... reversed: left, right, node

print(postorder_iter(bst))
```
```text
[1, 3, 2, 5, 7, 6, 4]
```

**Way 2: one stack and a `last` pointer.** Look at the top node. If it has an unvisited right child, go there. Otherwise, all its children are done: visit it. The variable `last` remembers the node just visited, so we do not enter the same right subtree twice.

```python
def postorder_iter2(root):
    out, stack, cur, last = [], [], root, None
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        top = stack[-1]
        if top.right and top.right is not last:
            cur = top.right              # the right subtree has not been done yet
        else:
            out.append(top.val)          # both subtrees are done
            last = stack.pop()
    return out

print(postorder_iter2(bst))
```
```text
[1, 3, 2, 5, 7, 6, 4]
```

### One template for all three

There is a trick that makes the three orders look alike. Put on the stack **pairs** `(node, done)`. A pair with `done = False` means "expand this node later"; `done = True` means "visit this node now". When you pop an unexpanded node, you push its three parts **in the reverse of the order you want to see them**.

```python
def traverse(root, order):
    out = []
    stack = [(root, False)]
    while stack:
        node, done = stack.pop()
        if node is None:
            continue
        if done:
            out.append(node.val)
        elif order == "pre":             # want: node, left, right  -> push reversed
            stack += [(node.right, False), (node.left, False), (node, True)]
        elif order == "in":              # want: left, node, right
            stack += [(node.right, False), (node, True), (node.left, False)]
        else:                            # post: left, right, node
            stack += [(node, True), (node.right, False), (node.left, False)]
    return out

for order in ("pre", "in", "post"):
    print(order, traverse(bst, order))
```
```text
pre [4, 2, 1, 3, 6, 5, 7]
in [1, 2, 3, 4, 5, 6, 7]
post [1, 3, 2, 5, 7, 6, 4]
```

The only line that differs between the three orders is the position of `(node, True)`. This is the version to use when you forget which iterative form is which.

### Are they right?

Compare all the versions with the recursive ones on many random trees. First, a helper that builds a **random tree** with a given number of nodes (we reuse it in later sections).

```python
import random

def random_tree(rng, n, lo=0, hi=9):
    """A random binary tree with n nodes and random values in [lo, hi]."""
    if n == 0:
        return None
    root = TreeNode(rng.randint(lo, hi))
    free = [(root, "left"), (root, "right")]          # empty child slots
    for _ in range(n - 1):
        i = rng.randrange(len(free))
        free[i], free[-1] = free[-1], free[i]
        node, side = free.pop()
        child = TreeNode(rng.randint(lo, hi))
        setattr(node, side, child)
        free += [(child, "left"), (child, "right")]
    return root

rng = random.Random(10)
ok = True
for _ in range(400):
    t = random_tree(rng, rng.randint(0, 12))
    for name, rec, it in (("pre", preorder, preorder_iter), ("in", inorder, inorder_iter),
                          ("post", postorder, postorder_iter)):
        expected = []
        rec(t, expected)
        ok &= it(t) == expected == traverse(t, name)
    expected = []
    postorder(t, expected)
    ok &= postorder_iter2(t) == expected
print("400 random trees: all iterative versions equal the recursive ones:", bool(ok))
print("iterative inorder on a skewed tree of 5000 nodes:", len(inorder_iter(skewed(5000))), "values")
```
```text
400 random trees: all iterative versions equal the recursive ones: True
iterative inorder on a skewed tree of 5000 nodes: 5000 values
```

### A word about Morris traversal

There is a famous trick, **Morris traversal**, that does an inorder walk with `O(1)` extra space (no stack, no recursion) by temporarily changing `right` pointers of leaves, then restoring them. It is clever and not needed for this course; it is listed in the further reading.

**Predict the output 3.** For the tree `[1, None, 2, 3]` (a root `1` with only a right child `2`, whose left child is `3`), what do the preorder, inorder and postorder give?

<details><summary>Answer</summary>

```python
t = build_tree([1, None, 2, 3])
print(traverse(t, "pre"), traverse(t, "in"), traverse(t, "post"))
```
```text
[1, 2, 3] [1, 3, 2] [3, 2, 1]
```

Preorder: `1`, then the right subtree `2, 3`. Inorder: no left subtree for `1`, so `1` first; then the right subtree in inorder: its left child `3`, then `2`, giving `1, 3, 2`. Postorder: the right subtree in postorder (`3`, then `2`), then the root: `3, 2, 1`.

</details>

## 6. Level order (breadth-first)

The depth-first orders go deep before they go wide. A **level-order** traversal visits the tree one level at a time: the root, then all nodes of depth 1 from left to right, then depth 2, and so on. It uses a **queue** (dsa.08), because the nodes found first must be handled first.

```python
def level_order(root):
    if root is None:
        return []
    levels, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):              # exactly the nodes of this level
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels

print(level_order(example))
print(level_order(bst))
print(level_order(None))
```
```text
[[3], [9, 20], [15, 7]]
[[4], [2, 6], [1, 3, 5, 7]]
[]
```

The key detail is `for _ in range(len(queue))`: read the size of the queue **before** the loop starts, so that you handle only the nodes of the current level while their children go to the back of the queue.

Once you have the levels, many questions become short:

```python
def right_side_view(root):
    """What you see standing on the right: the last node of each level."""
    return [level[-1] for level in level_order(root)]

def level_averages(root):
    return [sum(level) / len(level) for level in level_order(root)]

def bottom_up(root):
    return level_order(root)[::-1]

def zigzag(root):
    return [level if i % 2 == 0 else level[::-1] for i, level in enumerate(level_order(root))]

big = build_tree([1, 2, 3, 4, None, None, 5])
print(right_side_view(big))
print(level_averages(example))
print(bottom_up(example))
print(zigzag(build_tree([1, 2, 3, 4, 5, 6, 7])))
```
```text
[1, 3, 5]
[3.0, 14.5, 11.0]
[[15, 7], [9, 20], [3]]
[[1], [3, 2], [4, 5, 6, 7]]
```

In `big`, the levels are `[1]`, `[2, 3]`, `[4, 5]`, and the last node of each level is `1`, `3`, `5`. The right side view keeps the **last node of each level**, whichever side of the tree it hangs on. So a node on the left shows up when nothing is to its right on that level:

```python
print(right_side_view(build_tree([1, 2, 3, 4])))
```
```text
[1, 3, 4]
```

Here the level `[4]` has only the left-hand node `4`, which is what you see from the right at that depth.

### Level order with recursion

You can also build the levels with a depth-first function that passes the depth down. Because `left` is visited before `right`, each level's list is filled from left to right.

```python
def level_order_dfs(root):
    levels = []
    def go(node, depth):
        if node is None:
            return
        if depth == len(levels):
            levels.append([])                    # first time we reach this depth
        levels[depth].append(node.val)
        go(node.left, depth + 1)
        go(node.right, depth + 1)
    go(root, 0)
    return levels

print(level_order_dfs(example) == level_order(example))
```
```text
True
```

### Depth-first or breadth-first?

| | DFS (stack or recursion) | BFS (queue) |
|---|---|---|
| Order | goes deep first | one level at a time |
| Memory | `O(h)`: the height | `O(w)`: the widest level (up to `n/2`) |
| Good for | paths, subtree answers, backtracking | per-level answers, the **shortest** (fewest-edge) path, nearest leaf |

For a balanced tree, DFS uses very little memory and BFS can hold half the nodes. For a skewed tree the roles reverse: DFS holds the whole chain and BFS holds one node. Choose by the question: "per level" or "closest" means BFS; "along a path" or "whole subtree" means DFS.

**Try it 3.** Write `min_depth_bfs(root)`: the number of nodes on the shortest path from the root to a **leaf**, found with BFS. Why can BFS stop at the first leaf it meets?

<details><summary>Answer</summary>

```python
def min_depth_bfs(root):
    if root is None:
        return 0
    queue = deque([(root, 1)])
    while queue:
        node, depth = queue.popleft()
        if node.left is None and node.right is None:
            return depth                          # the first leaf found is the closest one
        if node.left:
            queue.append((node.left, depth + 1))
        if node.right:
            queue.append((node.right, depth + 1))

print(min_depth_bfs(example), min_depth_bfs(build_tree([1, None, 2])), min_depth_bfs(None))
```
```text
2 2 0
```

BFS visits nodes in order of depth, so the first leaf it finds has the smallest depth: nothing deeper can beat it. A DFS version must look at the whole tree.

</details>

## 7. Height, balance and diameter

### Height again, and the trap in "minimum depth"

You wrote `height` in section 3. The **minimum depth** looks like the same function with `min` instead of `max`, and that version is wrong.

```python
def min_depth_wrong(node):
    if node is None:
        return 0
    return 1 + min(min_depth_wrong(node.left), min_depth_wrong(node.right))

chain = build_tree([1, None, 2, None, 3])        # 1 -> 2 -> 3, all on the right
print(min_depth_wrong(chain), height(chain))
```
```text
1 3
```

It says `1`, but the only leaf is the node `3`, three nodes away. The node `1` has no left child, so `min_depth_wrong(None) = 0` wins the `min`, as if the missing child were a leaf. A **leaf is a node with no children at all**; a node with one child is *not* a leaf, and an absent child must not count as a path end.

```python
def min_depth(node):
    if node is None:
        return 0
    if node.left is None:                         # only a right child: the path must go right
        return 1 + min_depth(node.right)
    if node.right is None:
        return 1 + min_depth(node.left)
    return 1 + min(min_depth(node.left), min_depth(node.right))

print(min_depth(chain), min_depth(example), min_depth(bst), min_depth(None))
```
```text
3 2 3 0
```

### Is the tree balanced?

A tree is **height-balanced** if, for every node, the heights of its two subtrees differ by at most 1. The obvious solution calls `height` at every node, and it is slow, because `height` itself walks the subtree: the total is `O(n^2)` for a skewed shape, or `O(n log n)` for a balanced one.

The better solution does the check **while computing the height**, in one pass. The function returns the height, or `-1` as a signal meaning "this subtree is already unbalanced". This is "what does the call return?" with two kinds of answer in one number.

```python
def balanced_naive(node, visits):
    if node is None:
        return True
    def h(n):
        if n is None:
            return 0
        visits[0] += 1
        return 1 + max(h(n.left), h(n.right))
    return (abs(h(node.left) - h(node.right)) <= 1
            and balanced_naive(node.left, visits) and balanced_naive(node.right, visits))

def balanced_fast(root, visits):
    def check(node):                              # returns the height, or -1 if unbalanced
        if node is None:
            return 0
        visits[0] += 1
        left = check(node.left)
        if left == -1:
            return -1
        right = check(node.right)
        if right == -1 or abs(left - right) > 1:
            return -1
        return 1 + max(left, right)
    return check(root) != -1

perfect = build_tree(list(range(1, 1024)))        # a perfect tree with 1023 nodes
for func in (balanced_naive, balanced_fast):
    visits = [0]
    print(f"{func.__name__:15} -> {func(perfect, visits)}, node visits: {visits[0]}")
print(balanced_fast(build_tree([1, 2, 2, 3, None, None, 3, 4, None, None, 4]), [0]))
print(balanced_fast(example, [0]))
```
```text
balanced_naive  -> True, node visits: 8194
balanced_fast   -> True, node visits: 1023
False
True
```

On a perfect tree of 1023 nodes the fast version visits each node once. The naive version re-walks subtrees at every level, and the count is several times larger (it grows like `n log n`). On a skewed or unbalanced tree the gap widens. The idea "do the check inside the function that already walks the tree" is worth remembering.

### The diameter

The **diameter** of a tree is the length (in edges) of the longest path between any two nodes. The path may or may not pass through the root. For each node, the longest path that has this node as its **highest point** goes down the deepest left branch and the deepest right branch: its length is `left_height + right_height` (with heights counted in nodes). The diameter is the maximum of that number over all nodes.

Here the function **returns one thing** (the height, which the parent needs) but **records another** (the best diameter seen so far, in a variable shared by all calls). This pattern, "return for the parent, record for the answer", appears in many problems.

```python
def diameter(root):
    best = 0
    def go(node):
        nonlocal best
        if node is None:
            return 0
        left = go(node.left)
        right = go(node.right)
        best = max(best, left + right)            # a path with `node` as its highest point
        return 1 + max(left, right)               # what the parent needs: this node's height
    go(root)
    return best

print(diameter(example), diameter(bst), diameter(build_tree([1])), diameter(None), diameter(skewed(5)))
```
```text
3 4 0 0 4
```

For `example` (`3, 9, 20, 15, 7`) the longest path is `9 - 3 - 20 - 15`: three edges. For `bst` it is `1 - 2 - 4 - 6 - 7`: four edges. A chain of 5 nodes has a diameter of 4.

To be sure, compare it with a **brute force**: build the tree as an undirected graph, run a BFS from every node, and take the largest distance.

```python
def diameter_brute(root):
    if root is None:
        return 0
    adj, stack = {}, [root]
    while stack:                                   # collect the tree edges
        node = stack.pop()
        adj.setdefault(node, [])
        for child in (node.left, node.right):
            if child:
                adj[node].append(child)
                adj.setdefault(child, []).append(node)
                stack.append(child)
    best = 0
    for start in adj:
        dist, queue = {start: 0}, deque([start])
        while queue:
            node = queue.popleft()
            for nxt in adj[node]:
                if nxt not in dist:
                    dist[nxt] = dist[node] + 1
                    queue.append(nxt)
        best = max(best, max(dist.values()))
    return best

rng = random.Random(14)
ok = True
for _ in range(400):
    t = random_tree(rng, rng.randint(0, 14))
    ok &= diameter(t) == diameter_brute(t)
print("400 random trees: the diameter matches the brute force:", bool(ok))
```
```text
400 random trees: the diameter matches the brute force: True
```

**Predict the output 4.** What are `height`, `min_depth` and `diameter` of the tree `[1, 2, 3, 4, 5]`?

<details><summary>Answer</summary>

```python
t = build_tree([1, 2, 3, 4, 5])
print(height(t), min_depth(t), diameter(t))
```
```text
3 2 3
```

The height is 3 (`1 - 2 - 4`). The minimum depth is 2: the node `3` is a leaf at depth 2 (nodes counted). The diameter is 3 edges, for instance `4 - 2 - 1 - 3`, or `4 - 2 - 5`, which has only 2 edges, so the longer path through the root wins.

</details>

## 8. Paths

Many tree problems are about paths. Three different kinds exist, and each needs a slightly different design.

| Kind of path | Example | Style |
|---|---|---|
| root to leaf | "is there a root-to-leaf path with sum 22?" | pass the remaining sum **down** |
| any downward path (start and end anywhere, but always going down) | "count the downward paths with sum 8" | keep a running sum and a dictionary of earlier sums |
| any path (it may bend at a highest node) | "maximum path sum" | return the best downward gain, **record** the best bent path |

### Root to leaf: pass the target down

`has_path_sum(node, target)`: is there a path from `node` down to a **leaf** whose values add up to `target`? At each node, subtract its value and ask the same question of the children.

```python
def has_path_sum(node, target):
    if node is None:
        return False
    if node.left is None and node.right is None:        # a leaf: the path must end here
        return node.val == target
    remaining = target - node.val
    return has_path_sum(node.left, remaining) or has_path_sum(node.right, remaining)

t = build_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
print(has_path_sum(t, 22), has_path_sum(t, 26), has_path_sum(t, 5))
print(has_path_sum(build_tree([1, 2]), 1), has_path_sum(None, 0))
```
```text
True True False
False False
```

Two traps are in the last line. `[1, 2]` with target `1`: the root alone has the sum 1, but the root is **not a leaf** (it has the child `2`), so the answer is `False`. And the empty tree has no path at all, even for the target `0`. The leaf check is the whole point of the problem; writing `if node is None: return target == 0` gives wrong answers for these cases.

### All root-to-leaf paths: backtracking

This is the backtracking template of dsa.07 on a tree: add the node to a `path` list, recurse, and remove it again. When we reach a leaf, store a **copy** of the path.

```python
def root_to_leaf_paths(root):
    result, path = [], []

    def go(node):
        if node is None:
            return
        path.append(node.val)                            # choose
        if node.left is None and node.right is None:
            result.append(path[:])                       # a COPY of the path
        else:
            go(node.left)
            go(node.right)
        path.pop()                                       # un-choose

    go(root)
    return result

print(root_to_leaf_paths(example))
print(["->".join(map(str, p)) for p in root_to_leaf_paths(bst)])
```
```text
[[3, 9], [3, 20, 15], [3, 20, 7]]
['4->2->1', '4->2->3', '4->6->5', '4->6->7']
```

Compare with the recursion in dsa.07: there, a loop chose the next item; here the "choices" are just left and right. The tree is the search tree.

### Sum of root-to-leaf numbers

Each root-to-leaf path of digits is a number (`1 -> 2 -> 3` is `123`). Add them all. Pass the number built so far down: at each step `acc = acc * 10 + node.val`.

```python
def sum_numbers(node, acc=0):
    if node is None:
        return 0
    acc = acc * 10 + node.val
    if node.left is None and node.right is None:
        return acc
    return sum_numbers(node.left, acc) + sum_numbers(node.right, acc)

print(sum_numbers(build_tree([1, 2, 3])), sum_numbers(build_tree([4, 9, 0, 5, 1])))
```
```text
25 1026
```

`[1, 2, 3]` has the paths `12` and `13`: sum 25. `[4, 9, 0, 5, 1]` has `495`, `491` and `40`: sum 1026.

### Any downward path: prefix sums and a dictionary

Count the downward paths (from any node to any descendant, not necessarily to a leaf) whose sum equals `target`. The nodes may be negative.

The idea comes from the prefix sums of dsa.03 and the dictionary of dsa.04. Along the way from the root to the current node, let `running` be the sum of the values so far. A downward path ending here has sum `target` exactly when an earlier point on the same root path had the running sum `running - target`. So keep a dictionary `counts` of how often each running sum has appeared on the **current root path**. When you leave a node, take its running sum back out (backtracking again).

```python
def path_sum_count(root, target):
    counts = {0: 1}                                     # the empty prefix
    total = 0

    def go(node, running):
        nonlocal total
        if node is None:
            return
        running += node.val
        total += counts.get(running - target, 0)        # paths that end at this node
        counts[running] = counts.get(running, 0) + 1    # choose
        go(node.left, running)
        go(node.right, running)
        counts[running] -= 1                            # un-choose

    go(root, 0)
    return total

t = build_tree([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1])
print(path_sum_count(t, 8))
```
```text
3
```

Time `O(n)`, space `O(h)` for the recursion plus the dictionary. The slow way, starting a downward walk from every node, is `O(n * h)`. Test the fast version against it:

```python
def path_sum_count_slow(root, target):
    def from_here(node, remaining):
        if node is None:
            return 0
        remaining -= node.val
        return (remaining == 0) + from_here(node.left, remaining) + from_here(node.right, remaining)
    if root is None:
        return 0
    return (from_here(root, target) + path_sum_count_slow(root.left, target)
            + path_sum_count_slow(root.right, target))

rng = random.Random(17)
ok = True
for _ in range(400):
    t = random_tree(rng, rng.randint(0, 12), -4, 6)
    target = rng.randint(-4, 8)
    ok &= path_sum_count(t, target) == path_sum_count_slow(t, target)
print("400 random trees with negative values agree:", bool(ok))
```
```text
400 random trees with negative values agree: True
```

### Any path: the maximum path sum

Now the path may go **up and then down**: it has a highest node, with a branch going down on each side. Find the maximum sum of any non-empty path. Again the function **returns** something for its parent and **records** the answer.

- What the parent can use: a path that goes straight down from this node, which is `node.val + max(0, best_left_gain, best_right_gain)` (a branch with a negative gain is simply not taken).
- What we record: a path that bends at this node, `node.val + left_gain + right_gain` (both gains clipped at 0).

```python
def max_path_sum(root):
    best = float("-inf")

    def gain(node):
        """Best sum of a path that starts at `node` and goes down (at least `node` itself)."""
        nonlocal best
        if node is None:
            return 0
        left = max(0, gain(node.left))              # drop a negative branch
        right = max(0, gain(node.right))
        best = max(best, node.val + left + right)   # a path that bends at this node
        return node.val + max(left, right)          # the parent can only continue ONE way down

    gain(root)
    return best

print(max_path_sum(build_tree([1, 2, 3])))
print(max_path_sum(build_tree([-10, 9, 20, None, None, 15, 7])))
print(max_path_sum(build_tree([-3])), max_path_sum(build_tree([2, -1])))
```
```text
6
42
-3 2
```

The last two results show why the best path need not contain the root, and why we cannot use `0` as the initial `best`: a tree of one negative node must return that negative number. The key sentence: **the value we return (one branch) differs from the value we record (two branches)**, because a parent cannot extend a path that has already bent.

A brute-force check: take every node as a starting point, and add up values over every path in the undirected tree.

```python
def max_path_sum_brute(root):
    adj, stack = {}, [root]
    while stack:
        node = stack.pop()
        adj.setdefault(node, [])
        for child in (node.left, node.right):
            if child:
                adj[node].append(child)
                adj.setdefault(child, []).append(node)
                stack.append(child)
    best = float("-inf")
    for start in adj:
        todo = [(start, None, start.val)]
        while todo:
            node, parent, total = todo.pop()
            best = max(best, total)
            for nxt in adj[node]:
                if nxt is not parent:
                    todo.append((nxt, node, total + nxt.val))
    return best

rng = random.Random(19)
ok = True
for _ in range(400):
    t = random_tree(rng, rng.randint(1, 12), -6, 6)
    ok &= max_path_sum(t) == max_path_sum_brute(t)
print("400 random trees: the maximum path sum matches the brute force:", bool(ok))
```
```text
400 random trees: the maximum path sum matches the brute force: True
```

**Try it 4.** Write `longest_univalue_path(root)`: the length in edges of the longest path in which all nodes have the same value. Which of the three styles of this section does it follow?

<details><summary>Answer</summary>

It follows the third style (return one branch, record the bent path). A node extends its left branch only if the left child has the same value, and the same on the right.

```python
def longest_univalue_path(root):
    best = 0
    def go(node):                                    # returns the longest same-value path going DOWN (in edges)
        nonlocal best
        if node is None:
            return 0
        left, right = go(node.left), go(node.right)
        left_len = left + 1 if node.left and node.left.val == node.val else 0
        right_len = right + 1 if node.right and node.right.val == node.val else 0
        best = max(best, left_len + right_len)       # a bent path through this node
        return max(left_len, right_len)
    go(root)
    return best

print(longest_univalue_path(build_tree([5, 4, 5, 1, 1, None, 5])))
print(longest_univalue_path(build_tree([1, 4, 5, 4, 4, None, 5])))
```
```text
2
2
```

In the first tree, the longest same-value path is `5 - 5 - 5` along the right side: 2 edges. In the second, it is `4 - 4 - 4`: through the left child, 2 edges.

</details>

## 9. Binary search trees

You learned binary search in dsa.06: in a **sorted array**, compare with the middle and throw away half. A **binary search tree (BST)** brings that idea to a tree, so you can also **insert and delete** in `O(log n)` without shifting an array.

### The rule

A binary tree is a BST if, for **every** node:

- all values in its **left** subtree are **smaller** than the node's value, and
- all values in its **right** subtree are **larger**.

```text
        4                  Everything left of 4 is smaller (1, 2, 3).
      /   \                Everything right of 4 is larger (5, 6, 7).
     2     6               The same rule holds inside every subtree:
    / \   / \              for 2: left {1} < 2 < right {3}.
   1   3 5   7
```

Two consequences you will use again and again:

1. **Search is binary search.** At each node, compare the key: smaller -> go left; larger -> go right; equal -> found. You discard a whole subtree with one comparison.
2. **An inorder traversal visits the values in sorted order**, because it handles the left subtree (all smaller), then the node, then the right subtree (all larger). We saw this in section 4.

In this chapter the values in a BST are **distinct** (duplicates need a rule such as "equal goes right", which varies between problems; read the statement).

### Search, minimum and maximum

```python
def search(root, key):
    cur = root
    while cur:
        if key == cur.val:
            return cur
        cur = cur.left if key < cur.val else cur.right
    return None

def find_min(root):
    while root.left:
        root = root.left            # the smallest value is the leftmost node
    return root

def find_max(root):
    while root.right:
        root = root.right
    return root

print(search(bst, 5).val, search(bst, 8), find_min(bst).val, find_max(bst).val)
```
```text
5 None 1 7
```

Each step moves down one level, so the cost is `O(h)`, where `h` is the height. For a balanced tree that is `O(log n)`.

### Insert

Walk down as in a search until you fall off the tree; the new node goes in that empty place. The recursive version returns the (possibly new) root of each subtree and reattaches it, which keeps the code short.

```python
def insert(root, key):
    if root is None:
        return TreeNode(key)                 # found the empty place
    if key < root.val:
        root.left = insert(root.left, key)   # reattach: the subtree may be new
    elif key > root.val:
        root.right = insert(root.right, key)
    return root                              # equal key: already there, ignore

tree = None
for key in (5, 3, 8, 1, 4, 7, 9, 2):
    tree = insert(tree, key)
print(show_tree(tree))
print(to_level_list(tree))
```
```text
        9
    8
        7
5
        4
    3
            2
        1
[5, 3, 8, 1, 4, 7, 9, None, 2]
```

Notice that the **shape** depends on the **order** of the insertions. The same keys inserted in a different order give a different tree.

### Delete: three cases

Deleting is the hard one. First find the node, then:

1. **A leaf:** just remove it (replace it by `None`).
2. **One child:** replace the node by that child. The child's whole subtree moves up.
3. **Two children:** you cannot give two children to the parent. Instead, replace the node's *value* by its **inorder successor**, the smallest value in the right subtree (the next number in sorted order), and then delete that successor node from the right subtree. The successor has no left child (it is the leftmost), so deleting it is case 1 or 2. (The inorder predecessor, the largest on the left, works equally well.)

```python
def delete(root, key):
    if root is None:
        return None
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:                                         # this is the node to delete
        if root.left is None:                     # cases 1 and 2: at most a right child
            return root.right
        if root.right is None:                    # case 2: only a left child
            return root.left
        successor = find_min(root.right)          # case 3: two children
        root.val = successor.val
        root.right = delete(root.right, successor.val)
    return root

tree = None
for key in (5, 3, 8, 1, 4, 7, 9, 2):
    tree = insert(tree, key)
for key in (4, 1, 5, 42):
    tree = delete(tree, key)
    print(f"after delete {key:>2}:", to_level_list(tree))
```
```text
after delete  4: [5, 3, 8, 1, None, 7, 9, None, 2]
after delete  1: [5, 3, 8, 2, None, 7, 9]
after delete  5: [7, 3, 8, 2, None, None, 9]
after delete 42: [7, 3, 8, 2, None, None, 9]
```

Follow the three real cases above. Deleting `4` (a leaf) just removes it. Deleting `1` (one child, `2`) lifts `2` into its place. Deleting `5`, the root with two children, copies the successor `7` into the root and removes the old `7`. Deleting `42`, which is not in the tree, changes nothing.

The two bugs people write: forgetting the assignment (`delete(root.left, key)` without `root.left = ...`, so the removal is lost), and forgetting to remove the successor node after copying its value (so the value is now in the tree twice).

### Check it against a set

How do we trust `insert` and `delete`? Run thousands of random operations on both the BST and a Python `set`, and after every step check: the inorder traversal equals `sorted(model)`, which is both the right contents **and** a proof that the BST rule still holds (it is sorted).

```python
import random

rng = random.Random(23)
tree, model = None, set()
ok = True
for _ in range(4000):
    key = rng.randint(0, 40)
    op = rng.choice(["ins", "del", "find"])
    if op == "ins":
        tree = insert(tree, key); model.add(key)
    elif op == "del":
        tree = delete(tree, key); model.discard(key)
    else:
        ok &= (search(tree, key) is not None) == (key in model)
    out = []
    inorder(tree, out)
    ok &= out == sorted(model)
print("4000 random operations: the BST always matches the set and stays sorted:", bool(ok))
```
```text
4000 random operations: the BST always matches the set and stays sorted: True
```

### Why the order of insertion matters: the shape

Insert the numbers 0 to 499 in a random order, and then in sorted order:

```python
rng = random.Random(5)
keys = list(range(500))
shuffled = keys[:]
rng.shuffle(shuffled)

def build_bst(sequence):
    root = None
    for k in sequence:
        root = insert(root, k)
    return root

print("random order :", height(build_bst(shuffled)))
print("sorted order :", height(build_bst(keys)))
```
```text
random order : 19
sorted order : 500
```

Sorted input gives a chain: every key goes to the right of the previous one, the height is 500, and search is as slow as walking a linked list. Random input gives a height that is a small multiple of `log2(500)` (about 9). This is the problem that **balanced trees** (section 14) solve: they keep the height near `log n` whatever the order.

### Is this tree a BST? The classic mistake

A natural but wrong idea: "check that each node is larger than its left child and smaller than its right child." That checks the children only. The BST rule is about **whole subtrees**.

```python
def is_valid_wrong(node):
    if node is None:
        return True
    if node.left and node.left.val >= node.val:
        return False
    if node.right and node.right.val <= node.val:
        return False
    return is_valid_wrong(node.left) and is_valid_wrong(node.right)

bad = build_tree([5, 1, 6, None, None, 3, 7])
print(show_tree(bad))
print(is_valid_wrong(bad))
```
```text
        7
    6
        3
5
    1
True
```

The node `3` is a child of `6`, and `3 < 6`, so the local check is happy. But `3` sits in the right subtree of `5`, so it must be larger than `5`. The tree is **not** a BST.

**Fix 1: pass the allowed range down.** Every node must lie strictly between a lower bound and an upper bound that come from its ancestors. Going left sets a new upper bound (the node's value); going right sets a new lower bound.

```python
def is_valid_bst(node, lo=None, hi=None):
    if node is None:
        return True
    if lo is not None and node.val <= lo:
        return False
    if hi is not None and node.val >= hi:
        return False
    return is_valid_bst(node.left, lo, node.val) and is_valid_bst(node.right, node.val, hi)

print(is_valid_bst(bad), is_valid_bst(bst), is_valid_bst(None))
```
```text
False True True
```

We use `None` for "no bound yet", not `float("-inf")`, so that the code works for any comparable values.

**Fix 2: use the inorder property.** A tree is a BST exactly when its inorder traversal is **strictly increasing**. With the iterative inorder (section 5) we can compare each value with the previous one and stop at the first violation.

```python
def is_valid_bst_inorder(root):
    prev = None
    stack, cur = [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        if prev is not None and cur.val <= prev:       # not strictly increasing
            return False
        prev = cur.val
        cur = cur.right
    return True

print(is_valid_bst_inorder(bad), is_valid_bst_inorder(bst))
```
```text
False True
```

Test all three functions against a definition-based brute force on many trees: some random (mostly invalid), some real BSTs, some real BSTs with two values swapped.

```python
def is_valid_brute(node):
    if node is None:
        return True
    left, right = [], []
    inorder(node.left, left)
    inorder(node.right, right)
    return (all(v < node.val for v in left) and all(v > node.val for v in right)
            and is_valid_brute(node.left) and is_valid_brute(node.right))

def all_nodes(root):
    out, stack = [], [root] if root else []
    while stack:
        n = stack.pop(); out.append(n)
        stack += [c for c in (n.left, n.right) if c]
    return out
```

```python
rng = random.Random(29)
ok, valid_count = True, 0
for i in range(600):
    if i % 3 == 0:
        t = random_tree(rng, rng.randint(0, 9), 0, 6)
    else:
        t = build_bst(rng.sample(range(30), rng.randint(0, 9)))
        if i % 3 == 2 and t and (t.left or t.right):     # corrupt a valid BST: swap two values
            nodes = all_nodes(t)
            a, b = rng.sample(nodes, 2) if len(nodes) > 1 else (nodes[0], nodes[0])
            a.val, b.val = b.val, a.val
    truth = is_valid_brute(t)
    valid_count += truth
    ok &= is_valid_bst(t) == is_valid_bst_inorder(t) == truth
print("600 trees: both validators match the brute force:", bool(ok), "| valid ones:", valid_count)
```
```text
600 trees: both validators match the brute force: True | valid ones: 282
```

### Order questions: k-th smallest, successor, floor and ceiling

Because the inorder is sorted, **the k-th smallest** is the k-th node visited by an inorder walk. Stop as soon as you have it: `O(h + k)`.

```python
def kth_smallest(root, k):
    stack, cur = [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.right
    return None                                    # fewer than k nodes

print([kth_smallest(bst, k) for k in range(1, 9)])
```
```text
[1, 2, 3, 4, 5, 6, 7, None]
```

If the tree changes often and you must answer "k-th smallest" many times, store the **size of each subtree** in every node. Then at a node you compare `k` with the size of the left subtree and go left or right, `O(h)` per query. This is called an *order-statistic tree*.

The **inorder successor** of a key (the smallest value strictly greater than it) is found without any stack: walk down from the root, and every time you go **left**, remember the node you left behind. That node is a candidate for the successor.

```python
def successor(root, key):
    best = None
    cur = root
    while cur:
        if key < cur.val:
            best = cur                  # a possible answer; look for a smaller one on the left
            cur = cur.left
        else:
            cur = cur.right             # key >= cur.val: the answer must be larger, so go right
    return best.val if best else None

def ceiling(root, key):                 # smallest value >= key
    best = None
    cur = root
    while cur:
        if key == cur.val:
            return cur.val
        if key < cur.val:
            best = cur
            cur = cur.left
        else:
            cur = cur.right
    return best.val if best else None

def floor(root, key):                   # largest value <= key
    best = None
    cur = root
    while cur:
        if key == cur.val:
            return cur.val
        if key > cur.val:
            best = cur
            cur = cur.right
        else:
            cur = cur.left
    return best.val if best else None

sparse = build_bst([20, 10, 30, 5, 15, 25, 40])
for key in (5, 12, 40, 41, 0):
    print(f"key {key:>2}: successor {successor(sparse, key)}, floor {floor(sparse, key)}, ceiling {ceiling(sparse, key)}")
```
```text
key  5: successor 10, floor 5, ceiling 5
key 12: successor 15, floor 10, ceiling 15
key 40: successor None, floor 40, ceiling 40
key 41: successor None, floor 40, ceiling None
key  0: successor 5, floor None, ceiling 5
```

Check these with the `bisect` module (dsa.06) on the sorted values:

```python
import bisect

values = sorted([20, 10, 30, 5, 15, 25, 40])
ok = True
for key in range(-2, 45):
    i = bisect.bisect_right(values, key)               # values[i] is the first value > key
    ok &= successor(sparse, key) == (values[i] if i < len(values) else None)
    j = bisect.bisect_left(values, key)                # values[j] is the first value >= key
    ok &= ceiling(sparse, key) == (values[j] if j < len(values) else None)
    k = bisect.bisect_right(values, key)               # values[k-1] is the last value <= key
    ok &= floor(sparse, key) == (values[k - 1] if k > 0 else None)
print("successor, floor and ceiling agree with bisect for every key:", bool(ok))
```
```text
successor, floor and ceiling agree with bisect for every key: True
```

### Range queries with pruning

Sum the values in the range `[lo, hi]`. The BST lets you **prune** (dsa.07): if the node's value is below `lo`, nothing on its left can be in the range, so skip the left subtree; if it is above `hi`, skip the right subtree.

```python
def range_sum(root, lo, hi, visits):
    if root is None:
        return 0
    visits[0] += 1
    if root.val < lo:
        return range_sum(root.right, lo, hi, visits)       # everything on the left is too small
    if root.val > hi:
        return range_sum(root.left, lo, hi, visits)        # everything on the right is too big
    return (root.val + range_sum(root.left, lo, hi, visits)
            + range_sum(root.right, lo, hi, visits))

rng = random.Random(8)
many = list(range(1000))
rng.shuffle(many)
big_bst = build_bst(many)
visits = [0]
print(range_sum(big_bst, 100, 110, visits), sum(range(100, 111)))
print("nodes visited:", visits[0], "of", len(many))
```
```text
1155 1155
nodes visited: 23 of 1000
```

The answer is right (the sum of 100 to 110), and the search touched only a small part of the 1000 nodes: the path down to the range, plus the range itself. Cost: `O(h + number of values in the range)`.

### An iterator over a BST

How do you walk a BST one value at a time, with `O(h)` memory, and `O(1)` average time per step? Keep the stack of the iterative inorder as the *state* of the iterator: the stack holds the path of nodes still waiting. `next()` pops the top and pushes the left spine of its right child.

```python
class BSTIterator:
    def __init__(self, root):
        self.stack = []
        self._push_left(root)

    def _push_left(self, node):
        while node:
            self.stack.append(node)
            node = node.left

    def has_next(self):
        return bool(self.stack)

    def next(self):
        node = self.stack.pop()
        self._push_left(node.right)
        return node.val

it = BSTIterator(bst)
print([it.next() for _ in range(3)], it.has_next())
rest = []
while it.has_next():
    rest.append(it.next())
print(rest)
```
```text
[1, 2, 3] True
[4, 5, 6, 7]
```

One `next()` may push many nodes, but every node is pushed once and popped once in the whole walk, so the *average* cost is `O(1)` (the same amortised argument as in dsa.08).

**Predict the output 5.** After these operations, what is the level-order list of the tree?

```python
tree = None
for key in (50, 30, 70, 20, 40, 60, 80):
    tree = insert(tree, key)
tree = delete(tree, 30)
print(to_level_list(tree))
```

<details><summary>Answer</summary>

```text
[50, 40, 70, 20, None, 60, 80]
```

Before the delete, the tree is perfect: `50` with `30` and `70`, and below them `20, 40, 60, 80`. The node `30` has two children (`20` and `40`). Its inorder successor is the smallest value of its right subtree: `40`. So `40` is copied into the node, and the old `40` leaf is removed. The result is `50` with children `40` and `70`, and `40` keeps the left child `20`.

</details>

**Try it 5.** Write `kth_largest(root, k)` in `O(h + k)`. (Hint: what is the mirror image of an inorder walk?)

<details><summary>Answer</summary>

Walk **reverse inorder**: right subtree, node, left subtree. That visits the values from largest to smallest.

```python
def kth_largest(root, k):
    stack, cur = [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.right
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.left
    return None

print([kth_largest(bst, k) for k in (1, 2, 7, 8)])
```
```text
[7, 6, 1, None]
```

</details>

## 10. The lowest common ancestor

The **lowest common ancestor (LCA)** of two nodes `p` and `q` is the lowest (deepest) node that has both of them in its subtree. A node counts as a descendant of itself, so if `p` is an ancestor of `q`, the LCA is `p`. For the tree `[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]`, the LCA of `5` and `1` is `3`, and the LCA of `5` and `4` is `5`.

### In any binary tree

Use the "what does the call return?" method. Define:

> `lca(node, p, q)` returns `p` or `q` if exactly one of them is in the subtree of `node` (the one that is there), `None` if none of them is, and the LCA if both are.

- If `node` is `None`, return `None`.
- If `node` *is* `p` or `q`, return `node` (it is the answer for this subtree, assuming the other, if present, is below it).
- Ask both children. If **both** return something, then `p` is on one side and `q` on the other, so `node` is the LCA. If only one returns something, pass it up.

```python
def find(root, val):
    stack = [root] if root else []
    while stack:
        n = stack.pop()
        if n.val == val:
            return n
        stack += [c for c in (n.left, n.right) if c]
    return None

def lca(node, p, q):
    if node is None or node is p or node is q:
        return node
    left = lca(node.left, p, q)
    right = lca(node.right, p, q)
    if left and right:
        return node                  # p and q are in different subtrees: split point
    return left or right             # both are on one side (or only one exists)

t = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
for a, b in ((5, 1), (5, 4), (6, 4), (7, 8)):
    print(a, b, "->", lca(t, find(t, a), find(t, b)).val)
```
```text
5 1 -> 3
5 4 -> 5
6 4 -> 5
7 8 -> 3
```

The function assumes both nodes exist in the tree. If one is missing, it returns the other one (with no sign of a problem). When the input cannot be trusted, first check that both nodes exist, or return a flag along with the node.

```python
t2 = build_tree([1, 2, 3])
ghost = TreeNode(99)                              # a node that is not in the tree
print(lca(t2, find(t2, 2), ghost).val)            # the "answer" is just node 2
```
```text
2
```

The time is `O(n)` (every node may be visited) and the space is `O(h)`.

### In a BST: use the order

In a BST you do not need to look at both sides. At each node compare with `p` and `q`:

- both smaller than the node -> the LCA is in the left subtree;
- both larger -> it is in the right subtree;
- otherwise they are split (or one equals the node) -> **this node is the LCA**.

```python
def lca_bst(root, p, q):
    cur = root
    while cur:
        if p.val < cur.val and q.val < cur.val:
            cur = cur.left
        elif p.val > cur.val and q.val > cur.val:
            cur = cur.right
        else:
            return cur
    return None

sparse = build_bst([20, 10, 30, 5, 15, 25, 40])
for a, b in ((5, 15), (5, 10), (25, 40), (5, 40)):
    print(a, b, "->", lca_bst(sparse, find(sparse, a), find(sparse, b)).val)
```
```text
5 15 -> 10
5 10 -> 10
25 40 -> 30
5 40 -> 20
```

This is `O(h)` time and `O(1)` space: one downward walk, like a search.

### With parent pointers: the linked-list intersection again

Suppose every node knows its parent. Then the path from `p` up to the root and the path from `q` up to the root are two linked lists that **share their tail** (the common ancestors). The LCA is where the two lists first meet: exactly the **intersection of two linked lists** from dsa.09, with the same "switch heads" trick.

```python
def parent_map(root):
    parent = {root: None}
    stack = [root]
    while stack:
        node = stack.pop()
        for child in (node.left, node.right):
            if child:
                parent[child] = node
                stack.append(child)
    return parent

def lca_with_parents(root, p, q):
    parent = parent_map(root)
    a, b = p, q
    while a is not b:
        a = parent[a] if a is not None else q        # after the root, continue on the other path
        b = parent[b] if b is not None else p
    return a

t = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
print(lca_with_parents(t, find(t, 7), find(t, 4)).val, lca_with_parents(t, find(t, 6), find(t, 8)).val)
```
```text
2 3
```

The two pointers walk the same total distance, so they meet at the LCA. If `p` is an ancestor of `q`, the pointer for `p` stands on `p` already when the other one arrives. A dictionary (dsa.04) stands in for the missing `parent` field; in problems where nodes have a `parent` link, use it directly.

### Distance between two nodes

Once you have the LCA, the number of edges between `p` and `q` is `depth(p) + depth(q) - 2 * depth(LCA)`: go up from each to the LCA.

```python
def depth_of(parent, node):
    d = 0
    while parent[node] is not None:
        node = parent[node]
        d += 1
    return d

def distance(root, p, q):
    parent = parent_map(root)
    ancestor = lca(root, p, q)
    return depth_of(parent, p) + depth_of(parent, q) - 2 * depth_of(parent, ancestor)

t = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
print(distance(t, find(t, 7), find(t, 8)), distance(t, find(t, 6), find(t, 4)), distance(t, find(t, 5), find(t, 5)))
```
```text
5 3 0
```

The path `7 - 2 - 5 - 3 - 1 - 8` has 5 edges. Between `6` and `4` there are `6 - 5 - 2 - 4`: 3 edges. A node to itself: 0.

### Check all three against a brute force

The brute force finds the path from the root to each node (a list of nodes) and takes the last node the two paths share.

```python
def relabel(root):
    """Give the nodes the distinct values 0..n-1 in preorder (the shape stays random)."""
    counter = [0]
    def go(node):
        if node is None:
            return
        node.val = counter[0]
        counter[0] += 1
        go(node.left)
        go(node.right)
    go(root)
    return root

def path_to(root, target):
    if root is None:
        return None
    if root is target:
        return [root]
    for child in (root.left, root.right):
        sub = path_to(child, target)
        if sub:
            return [root] + sub
    return None

def lca_brute(root, p, q):
    pa, pb = path_to(root, p), path_to(root, q)
    last = None
    for x, y in zip(pa, pb):
        if x is y:
            last = x
    return last
```

```python
rng = random.Random(31)
ok = True
for _ in range(400):
    t = relabel(random_tree(rng, rng.randint(1, 14)))
    nodes = all_nodes(t)
    p, q = rng.choice(nodes), rng.choice(nodes)
    expected = lca_brute(t, p, q)
    ok &= lca(t, p, q) is expected and lca_with_parents(t, p, q) is expected
for _ in range(400):
    t = build_bst(rng.sample(range(100), rng.randint(1, 14)))
    nodes = all_nodes(t)
    p, q = rng.choice(nodes), rng.choice(nodes)
    ok &= lca_bst(t, p, q) is lca_brute(t, p, q)
print("800 random trees: all LCA methods match the brute force:", bool(ok))
```
```text
800 random trees: all LCA methods match the brute force: True
```

**Predict the output 6.** In the tree `[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5]` (a BST), what is the LCA of `2` and `8`? Of `2` and `4`? Of `3` and `5`?

<details><summary>Answer</summary>

```python
t = build_bst([6, 2, 8, 0, 4, 7, 9, 3, 5])
for a, b in ((2, 8), (2, 4), (3, 5)):
    print(a, b, "->", lca_bst(t, find(t, a), find(t, b)).val)
```
```text
2 8 -> 6
2 4 -> 2
3 5 -> 4
```

For `2` and `8`: one is smaller than `6` and one is larger, so `6` splits them. For `2` and `4`: `4` is in the right subtree of `2`, and the walk stops at `2` (it equals one of the nodes: a node is its own descendant). For `3` and `5`: both smaller than `6`, both larger than `2`, then `4` splits them.

</details>

**Try it 6.** Why does `lca` return the right answer when `p` is an ancestor of `q`, although it never looks below `p`?

<details><summary>Answer</summary>

When the recursion reaches `p` it returns `p` immediately, without looking below it. If `q` is somewhere under `p`, we do not need to find it: `p` is by definition the lowest node containing both. The calls above `p` get `p` from one side and `None` from the other, so they pass `p` up unchanged. The case "both found" is only reached at a node that has `p` and `q` in different subtrees.

```python
t = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
print(lca(t, find(t, 5), find(t, 4)).val)
```
```text
5
```

</details>

## 11. Building and serialising trees

### Why one traversal is not enough

Is a tree determined by its preorder list? No. These two trees have the same preorder `[1, 2]`, but different shapes (`2` is the left child in one and the right child in the other).

```python
a = build_tree([1, 2])                       # 2 is the left child of 1
b = build_tree([1, None, 2])                 # 2 is the right child of 1
pre_a, pre_b, in_a, in_b = [], [], [], []
preorder(a, pre_a); preorder(b, pre_b)
inorder(a, in_a); inorder(b, in_b)
print("preorder:", pre_a, pre_b)
print("inorder :", in_a, in_b)
```
```text
preorder: [1, 2] [1, 2]
inorder : [2, 1] [1, 2]
```

The preorders are equal; the inorders differ. **Preorder plus inorder** (or **postorder plus inorder**) of a tree with distinct values determines the tree. The idea:

1. The first item of the preorder is the root. (In postorder, the last.)
2. Find the root in the inorder list. Everything to its left belongs to the left subtree, everything to its right to the right subtree.
3. Rebuild the left and right subtrees from the matching pieces.

To find the root in the inorder list in `O(1)`, make a dictionary `value -> index` (dsa.04). Then the whole construction is `O(n)`.

```python
def build_from_pre_in(preorder_vals, inorder_vals):
    index = {v: i for i, v in enumerate(inorder_vals)}
    next_root = iter(preorder_vals)               # hands out the roots in preorder

    def go(lo, hi):                               # build from inorder_vals[lo..hi]
        if lo > hi:
            return None
        val = next(next_root)                     # the next preorder item is this subtree's root
        node = TreeNode(val)
        mid = index[val]
        node.left = go(lo, mid - 1)               # left first: preorder lists it first
        node.right = go(mid + 1, hi)
        return node

    return go(0, len(inorder_vals) - 1)

t = build_from_pre_in([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
print(to_level_list(t))
```
```text
[3, 9, 20, None, None, 15, 7]
```

The order of the two recursive calls is important: the preorder lists the whole left subtree before the right one, so the left subtree must be built **first** to consume the right items from the iterator.

From **postorder and inorder** the root is the last item of the postorder. The right subtree comes just before it (in postorder `L, R, root`), so read the postorder from the end and build the **right** subtree first.

```python
def build_from_in_post(inorder_vals, postorder_vals):
    index = {v: i for i, v in enumerate(inorder_vals)}
    next_root = iter(reversed(postorder_vals))    # roots from the end of the postorder

    def go(lo, hi):
        if lo > hi:
            return None
        val = next(next_root)
        node = TreeNode(val)
        mid = index[val]
        node.right = go(mid + 1, hi)              # the RIGHT subtree is built first
        node.left = go(lo, mid - 1)
        return node

    return go(0, len(inorder_vals) - 1)

t = build_from_in_post([9, 3, 15, 20, 7], [9, 15, 7, 20, 3])
print(to_level_list(t))
```
```text
[3, 9, 20, None, None, 15, 7]
```

### A BST needs only one traversal

For a BST, the order rule replaces the inorder list: the preorder alone tells you the shape. The first value is the root; the following values smaller than it go left; then the larger ones go right. Do it in one pass with bounds, like `is_valid_bst`.

```python
def bst_from_preorder(values):
    pos = 0

    def go(lo, hi):
        nonlocal pos
        if pos == len(values) or not (lo < values[pos] < hi):
            return None                            # the next value does not belong in this range
        val = values[pos]
        pos += 1
        node = TreeNode(val)
        node.left = go(lo, val)                    # smaller values: bounded above by val
        node.right = go(val, hi)
        return node

    return go(float("-inf"), float("inf"))

t = bst_from_preorder([8, 5, 1, 7, 10, 12])
print(to_level_list(t))
```
```text
[8, 5, 10, 1, 7, None, 12]
```

### Serialisation: a tree to text and back

To save a tree to a file or send it over a network, we need a string from which the same tree can be rebuilt. **Preorder with markers for the missing children** does it: write `#` for `None`. The markers make the preorder unambiguous, because every node is followed by exactly its two subtrees.

```python
def serialize(root):
    out = []
    def go(node):
        if node is None:
            out.append("#")
            return
        out.append(str(node.val))
        go(node.left)
        go(node.right)
    go(root)
    return ",".join(out)

def deserialize(text):
    tokens = iter(text.split(","))
    def go():
        token = next(tokens)
        if token == "#":
            return None
        node = TreeNode(int(token))
        node.left = go()
        node.right = go()
        return node
    return go()

t = build_tree([1, 2, 3, None, None, 4, 5])
text = serialize(t)
print(text)
print(to_level_list(deserialize(text)))
print(repr(serialize(None)), deserialize("#"))
```
```text
1,2,#,#,3,4,#,#,5,#,#
[1, 2, 3, None, None, 4, 5]
'#' None
```

Reading the text: `1,2,#,#,3,4,#,#,5,#,#` means "node 1; its left subtree is node 2 with two empty children; its right subtree is node 3, whose left is node 4 (two empty children) and whose right is node 5 (two empty children)". The deserializer uses the same recursion as the serializer, and the iterator takes tokens in the same order.

The other common format is the **level-order list** with `None`, used by `build_tree` and `to_level_list` in this chapter. The two formats store the same information in different orders.

### Check the rebuilders on random trees

```python
rng = random.Random(37)
ok = True
for _ in range(400):
    t = relabel(random_tree(rng, rng.randint(0, 12)))          # distinct values, so traversals determine the tree
    pre, ino, post = [], [], []
    preorder(t, pre); inorder(t, ino); postorder(t, post)
    shape = to_level_list(t)
    ok &= to_level_list(build_from_pre_in(pre, ino)) == shape
    ok &= to_level_list(build_from_in_post(ino, post)) == shape
    ok &= to_level_list(deserialize(serialize(t))) == shape
    ok &= to_level_list(build_tree(shape)) == shape
for _ in range(200):
    t = build_bst(rng.sample(range(50), rng.randint(0, 10)))
    pre = []
    preorder(t, pre)
    ok &= to_level_list(bst_from_preorder(pre)) == to_level_list(t)
print("600 random trees: every builder reproduces the original tree:", bool(ok))
```
```text
600 random trees: every builder reproduces the original tree: True
```

### A sorted list to a balanced BST

Given a sorted list, build a BST whose height is as small as possible. Make the **middle** value the root; the left half becomes the left subtree and the right half the right subtree. This is binary search (dsa.06) used to *build* a tree.

```python
def sorted_to_bst(values):
    def go(lo, hi):                                # values[lo..hi)
        if lo >= hi:
            return None
        mid = (lo + hi) // 2
        node = TreeNode(values[mid])
        node.left = go(lo, mid)
        node.right = go(mid + 1, hi)
        return node
    return go(0, len(values))

t = sorted_to_bst(list(range(1, 11)))
out = []
inorder(t, out)
print(out == list(range(1, 11)), height(t), is_valid_bst(t), balanced_fast(t, [0]))
print(height(sorted_to_bst(list(range(1000)))), height(build_bst(list(range(500)))))
```
```text
True 4 True True
10 500
```

Ten values give a tree of height 4 (the best possible, as `2^3 - 1 < 10 <= 2^4 - 1`). A thousand values give height 10, compared with a height of 500 for the same idea done badly (inserting the sorted numbers one by one). This is what a balanced tree achieves automatically.

**Predict the output 7.** What does `serialize` give for the tree `[1, None, 2]`?

<details><summary>Answer</summary>

```python
print(serialize(build_tree([1, None, 2])))
```
```text
1,#,2,#,#
```

The root `1`; its left child is `None` (`#`); its right child is `2`, which has two empty children (`#,#`). That is `1,#,2,#,#`: five tokens for two nodes. A tree with `n` nodes always has `n + 1` empty slots, so the text has exactly `2n + 1` tokens.

</details>

**Try it 7.** The tree `[2, 1, 3]` is a BST. Build it from the preorder `[2, 1, 3]` with `bst_from_preorder`, and then explain why `bst_from_preorder([2, 3, 1])` builds a tree that is *not* the same as the tree `[2, 1, 3]` — and what that tree looks like.

<details><summary>Answer</summary>

```python
print(to_level_list(bst_from_preorder([2, 1, 3])))
print(to_level_list(bst_from_preorder([2, 3, 1])))
```
```text
[2, 1, 3]
[2, None, 3]
```

`[2, 3, 1]` is a different preorder: after the root `2`, the value `3` is larger, so it cannot go left; it goes right. Then `1` is smaller than `2`: it should go left, but we are already inside the right subtree (bounded below by `2`), so `1` does not fit there either. The function stops and the leftover `1` is never used. The preorder `[2, 3, 1]` is not the preorder of any BST: a valid BST preorder has every right-subtree value *after* the left-subtree values. The result `[2, None, 3]` is only a partial tree. Feeding the function an invalid preorder is the user's mistake; it does not check its input.

</details>

## 12. Comparing and reshaping trees

The tools of this chapter combine into short solutions for many "tree against tree" problems. In each, ask the question of section 3: *what does the call return?*

### Are two trees the same?

> `same_tree(a, b)` returns `True` if the two trees have the same shape and the same values.

Both empty: `True`. Exactly one empty: `False`. Otherwise the roots must match, and both pairs of subtrees must be the same.

```python
def same_tree(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a.val == b.val and same_tree(a.left, b.left) and same_tree(a.right, b.right)

print(same_tree(build_tree([1, 2, 3]), build_tree([1, 2, 3])))
print(same_tree(build_tree([1, 2]), build_tree([1, None, 2])))
print(same_tree(None, None), same_tree(None, build_tree([1])))
```
```text
True
False
True False
```

The second pair has the same values but a different shape (`2` is a left child in one, a right child in the other), so the answer is `False`. Comparing only the inorder lists would call them different too, but comparing only the *sets of values* would not. Always compare structure.

### Is the tree symmetric (a mirror of itself)?

A tree is symmetric if its left subtree is the mirror image of its right subtree. Mirror images compare **left with right and right with left**.

```python
def is_mirror(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a.val == b.val and is_mirror(a.left, b.right) and is_mirror(a.right, b.left)

def is_symmetric(root):
    return root is None or is_mirror(root.left, root.right)

print(is_symmetric(build_tree([1, 2, 2, 3, 4, 4, 3])))
print(is_symmetric(build_tree([1, 2, 2, None, 3, None, 3])))
```
```text
True
False
```

### Is one tree a subtree of another?

`is_subtree(root, sub)`: does some node of `root` start a subtree that is exactly the same as `sub`? Try `same_tree` at every node.

```python
def is_subtree(root, sub):
    if sub is None:
        return True
    if root is None:
        return False
    return same_tree(root, sub) or is_subtree(root.left, sub) or is_subtree(root.right, sub)

big = build_tree([3, 4, 5, 1, 2])
print(is_subtree(big, build_tree([4, 1, 2])))
print(is_subtree(build_tree([3, 4, 5, 1, 2, None, None, None, None, 0]), build_tree([4, 1, 2])))
```
```text
True
False
```

This is `O(n * m)` in the worst case (`n` nodes in the big tree, `m` in the small one). A faster approach serialises both trees (section 11) and searches for one string inside the other. That works only if the serialisation has **delimiters**. Here is the classic bug with no delimiters:

```python
def serialize_no_delimiter(node):
    if node is None:
        return "#"
    return str(node.val) + serialize_no_delimiter(node.left) + serialize_no_delimiter(node.right)

big = build_tree([12])
small = build_tree([2])
print(serialize_no_delimiter(big), serialize_no_delimiter(small))
print("2##" in serialize_no_delimiter(big))
print(is_subtree(big, small))
```
```text
12## 2##
True
False
```

The string `"2##"` appears inside `"12##"`, but the tree `[2]` is *not* a subtree of `[12]`: the digits `1` and `2` run together into `12`. Separating the values with commas is not enough either, because `"2,#,#"` is still a piece of `"12,#,#"`. The fix is to put a delimiter **in front of every token**, so a match can only start at a token boundary:

```python
big = build_tree([12])
small = build_tree([2])

def serialize_delim(node):
    if node is None:
        return ",#"
    return "," + str(node.val) + serialize_delim(node.left) + serialize_delim(node.right)

print(serialize_delim(big), serialize_delim(small))
print(serialize_delim(small) in serialize_delim(big))
print(serialize_delim(build_tree([4, 1, 2])) in serialize_delim(build_tree([3, 4, 5, 1, 2])))
```
```text
,12,#,# ,2,#,#
False
True
```

Now `",2,#,#"` is not found inside `",12,#,#"`, because the comma before the `2` is missing there. The real subtree `[4, 1, 2]` is found. A match always ends with a `#` (a one-character token), so it can never stop in the middle of a number. This method is `O(n + m)` with a good string search, compared with `O(n * m)` for the recursive check.

### Flatten a tree into a linked list

Rearrange the tree **in place** so that every node has only a right child, and the nodes follow the **preorder** order. For each node with a left subtree: find the last node of that left subtree (its rightmost node, the preorder predecessor of the node's right subtree), hang the current right subtree on it, move the left subtree to the right, and clear `left`.

```python
def flatten(root):
    cur = root
    while cur:
        if cur.left:
            last = cur.left
            while last.right:
                last = last.right              # the rightmost node of the left subtree
            last.right = cur.right             # the old right subtree goes after it
            cur.right = cur.left
            cur.left = None
        cur = cur.right                         # move on along the new right chain

t = build_tree([1, 2, 5, 3, 4, None, 6])
expected = []
preorder(t, expected)
flatten(t)
chain = []
node = t
while node:
    chain.append((node.val, node.left))
    node = node.right
print(expected)
print([v for v, _ in chain], all(left is None for _, left in chain))
```
```text
[1, 2, 3, 4, 5, 6]
[1, 2, 3, 4, 5, 6] True
```

No recursion and no extra memory: the tree becomes a linked list in the style of dsa.09, using the same `right` field as `next`.

### Count "good" nodes: information that goes down

A node is **good** if no node on the path from the root to it has a larger value. This is a top-down problem: pass the maximum seen so far as a parameter.

```python
def count_good(node, max_so_far=float("-inf")):
    if node is None:
        return 0
    good = 1 if node.val >= max_so_far else 0
    new_max = max(max_so_far, node.val)
    return good + count_good(node.left, new_max) + count_good(node.right, new_max)

print(count_good(build_tree([3, 1, 4, 3, None, 1, 5])), count_good(build_tree([3, 3, None, 4, 2])), count_good(None))
```
```text
4 3 0
```

### Check against a second implementation

For `same_tree`, `is_symmetric` and `is_subtree`, the second implementation compares the **level-order lists** (a different representation of the same tree).

```python
rng = random.Random(41)
ok = True
for _ in range(600):
    a = random_tree(rng, rng.randint(0, 6), 0, 2)
    b = random_tree(rng, rng.randint(0, 6), 0, 2)
    ok &= same_tree(a, b) == (to_level_list(a) == to_level_list(b))
    ok &= same_tree(a, a)
    mirrored = invert(build_tree(to_level_list(a)))                # an independent mirror copy
    ok &= is_mirror(a, mirrored)
    sub_found = any(same_tree(n, b) for n in all_nodes(a)) if b is not None else True
    ok &= is_subtree(a, b) == sub_found
print("600 random pairs: same_tree, is_mirror and is_subtree agree with the brute force:", bool(ok))
```
```text
600 random pairs: same_tree, is_mirror and is_subtree agree with the brute force: True
```

**Try it 8.** Write `compare_heights(a, b)` that returns `-1`, `0` or `1` when the tree `a` is shorter than, as high as, or taller than the tree `b`. Use only functions you already have.

<details><summary>Answer</summary>

```python
def compare_heights(a, b):
    ha, hb = height(a), height(b)
    return (ha > hb) - (ha < hb)

print(compare_heights(bst, example), compare_heights(example, bst), compare_heights(bst, bst), compare_heights(None, bst))
```
```text
0 0 0 -1
```

The expression `(x > y) - (x < y)` gives `1`, `0` or `-1`. It reuses `height` from section 3, a small example of building a new question from a solved one.

</details>

## 13. Other ways to store a tree

A binary tree of `TreeNode` objects is only one choice. Here are three others that you will meet.

### Trees with many children

A node can hold a **list of children** instead of exactly two. The ideas are the same: recursion over the children list, DFS with a stack, BFS with a queue.

```python
class NNode:
    def __init__(self, val, children=None):
        self.val = val
        self.children = children or []

def preorder_n(node):
    out = [node.val]
    for child in node.children:
        out += preorder_n(child)
    return out

def postorder_n(node):
    out = []
    for child in node.children:
        out += postorder_n(child)
    return out + [node.val]

def levels_n(root):
    levels, queue = [], deque([root])
    while queue:
        levels.append([n.val for n in queue])
        queue = deque(child for n in queue for child in n.children)
    return levels

def max_depth_n(node):
    return 1 + max((max_depth_n(c) for c in node.children), default=0)

tree = NNode(1, [NNode(3, [NNode(5), NNode(6)]), NNode(2), NNode(4)])
print(preorder_n(tree))
print(postorder_n(tree))
print(levels_n(tree), max_depth_n(tree))
```
```text
[1, 3, 5, 6, 2, 4]
[5, 6, 3, 2, 4, 1]
[[1], [3, 2, 4], [5, 6]] 3
```

There is no "inorder" for a node with three children: "between the left and the right" has no meaning. The `default=0` in `max` handles a leaf (a node with an empty list of children).

### A file system is a tree

Folders are inner nodes and files are leaves. A dictionary of dictionaries is a natural way to write one: a value that is a number is a file (its size), a value that is a dictionary is a folder. The total size of a folder is a **postorder** computation: you need the sizes of everything inside before you know its own.

```python
disk = {
    "src": {"main.py": 120, "utils": {"io.py": 40, "math.py": 55}},
    "README.md": 10,
    "docs": {},
}

def total_size(folder):
    return sum(total_size(item) if isinstance(item, dict) else item for item in folder.values())

def folder_sizes(folder, path=""):
    """{path: total size} for every folder, found by a postorder walk."""
    sizes = {}
    total = 0
    for name, item in folder.items():
        if isinstance(item, dict):
            sub = folder_sizes(item, f"{path}/{name}")
            sizes.update(sub)
            total += sub[f"{path}/{name}"]
        else:
            total += item
    sizes[path or "/"] = total
    return sizes

def print_tree(folder, indent=0):
    for name, item in sorted(folder.items()):
        print("  " * indent + name + ("/" if isinstance(item, dict) else f" ({item})"))
        if isinstance(item, dict):
            print_tree(item, indent + 1)

print_tree(disk)
print(total_size(disk))
print(folder_sizes(disk))
```
```text
README.md (10)
docs/
src/
  main.py (120)
  utils/
    io.py (40)
    math.py (55)
225
{'/src/utils': 95, '/src': 215, '/docs': 0, '/': 225}
```

The standard library does the same walk for real folders: `os.walk` and `pathlib.Path.rglob` (core.12) traverse the file-system tree.

### The parent array

Sometimes a tree arrives as a list where `parent[i]` is the parent of node `i` and the root has parent `-1`. This is compact and good for input files. Build the child lists in one pass and you are back to the usual tree.

```python
parent = [-1, 0, 0, 1, 1, 2]                       # node 0 is the root

children = [[] for _ in parent]
for node, p in enumerate(parent):
    if p != -1:
        children[p].append(node)

depth = [0] * len(parent)
order = deque([parent.index(-1)])
while order:                                       # BFS from the root fills the depths
    node = order.popleft()
    for c in children[node]:
        depth[c] = depth[node] + 1
        order.append(c)

print(children)
print(depth)
```
```text
[[1, 2], [3, 4], [5], [], [], []]
[0, 1, 1, 2, 2, 2]
```

### The array layout of a complete tree

A **complete** binary tree (all levels full except possibly the last, filled from the left) needs no pointers at all. Store the nodes in level order in a list. The children of the node at index `i` are at `2i + 1` and `2i + 2`, and the parent is at `(i - 1) // 2`.

```text
index:   0
        / \
       1   2          children of i: 2i+1, 2i+2
      / \ / \         parent of i:   (i-1)//2
     3  4 5  6
```

```python
tree_array = [4, 2, 6, 1, 3, 5, 7]                 # the level-order list of our BST

def left(i):  return 2 * i + 1
def right(i): return 2 * i + 2
def up(i):    return (i - 1) // 2

def inorder_array(a, i=0):
    if i >= len(a):
        return []
    return inorder_array(a, left(i)) + [a[i]] + inorder_array(a, right(i))

print(left(1), right(1), up(5))
print(inorder_array(tree_array))
```
```text
3 4 2
[1, 2, 3, 4, 5, 6, 7]
```

The index arithmetic replaces the pointers, saving memory and improving speed. This layout is how **heaps** are stored, the topic of the next module. It works well only for complete trees: a sparse tree would leave many empty slots.

### A prefix tree (a preview)

A **trie** stores words letter by letter. Each node has one child per letter, and a flag that says "a word ends here". Words that share a prefix share a path. A dictionary of dictionaries is enough:

```python
def trie_insert(root, word):
    node = root
    for ch in word:
        node = node.setdefault(ch, {})
    node["$"] = True                                # marks the end of a word

def trie_has_prefix(root, prefix):
    node = root
    for ch in prefix:
        if ch not in node:
            return False
        node = node[ch]
    return True

root = {}
for w in ("car", "card", "care", "dog"):
    trie_insert(root, w)
print(trie_has_prefix(root, "car"), trie_has_prefix(root, "cab"), "$" in root["c"]["a"]["r"])
```
```text
True False True
```

Looking up a word costs `O(length of the word)`, whatever the number of words stored.

## 14. Balanced trees: keeping the height small

Every BST operation costs `O(h)`. We saw in section 9 that sorted insertions make `h = n`, and then a search is a linear scan. We want trees that **keep their own height near `log n`**, whatever the order of the insertions. These are **self-balancing** trees. They fix the shape *after* each insertion or deletion, using a local rewiring called a **rotation**.

### Rotations

A rotation changes the shape of a small part of the tree while keeping the BST order. Take a node `y` with a left child `x`. A **right rotation** makes `x` the top, and `y` its right child. The right subtree of `x` (values between `x` and `y`) moves to become the left subtree of `y`, so the order is untouched.

```text
      y                      x
     / \                    / \
    x   C     rotate       A   y
   / \        right -->       / \
  A   B                      B   C

order before: A  x  B  y  C      order after: A  x  B  y  C   (the same)
```

A **left rotation** is the mirror image. A rotation changes only three pointers and costs `O(1)`.

### AVL trees

The first balanced tree (1962, by Adelson-Velsky and Landis). The rule: for **every** node, the heights of the left and the right subtree differ by **at most 1**. Each node stores its height. After an insertion, we go back up the path; at the first node where the difference becomes 2, we rotate. Four cases:

| Case | What happened | Fix |
|---|---|---|
| Left-left | new key went into the left subtree of the left child | one **right** rotation |
| Right-right | into the right subtree of the right child | one **left** rotation |
| Left-right | into the right subtree of the left child | left rotation on the child, then right rotation |
| Right-left | into the left subtree of the right child | right rotation on the child, then left rotation |

The code is short, because the four cases collapse into one `rebalance` function.

```python
class AVLNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.height = 1                      # a single node has height 1

def h(node):
    return node.height if node else 0

def update(node):
    node.height = 1 + max(h(node.left), h(node.right))

def balance_factor(node):
    return h(node.left) - h(node.right)      # positive: left-heavy

def rotate_right(y):
    x = y.left
    y.left = x.right                         # the middle subtree changes sides
    x.right = y
    update(y)                                # y is lower now: update it first
    update(x)
    return x                                 # x is the new top of this subtree

def rotate_left(x):
    y = x.right
    x.right = y.left
    y.left = x
    update(x)
    update(y)
    return y

def rebalance(node):
    update(node)
    balance = balance_factor(node)
    if balance > 1:                          # left-heavy
        if balance_factor(node.left) < 0:    # left-right case: first turn it into left-left
            node.left = rotate_left(node.left)
        return rotate_right(node)
    if balance < -1:                         # right-heavy
        if balance_factor(node.right) > 0:   # right-left case
            node.right = rotate_right(node.right)
        return rotate_left(node)
    return node

def avl_insert(node, key):
    if node is None:
        return AVLNode(key)
    if key < node.val:
        node.left = avl_insert(node.left, key)
    elif key > node.val:
        node.right = avl_insert(node.right, key)
    else:
        return node                          # duplicate: ignore
    return rebalance(node)                   # fix the shape on the way back up

# the three classic cases
for keys in ([1, 2, 3], [3, 1, 2], [1, 3, 2]):
    root = None
    for k in keys:
        root = avl_insert(root, k)
    print(keys, "->", to_level_list(root))
```
```text
[1, 2, 3] -> [2, 1, 3]
[3, 1, 2] -> [2, 1, 3]
[1, 3, 2] -> [2, 1, 3]
```

Each of the three insertions would make a chain of 3 nodes in an ordinary BST. In the AVL tree, each ends as the perfect tree `[2, 1, 3]`: the first case needs one left rotation, the second a double rotation (left-right), and the third a double rotation (right-left).

The two lines in `rotate_right` that update heights are the important ones: **update the lower node first**, because the upper node's height depends on it.

### The test: sorted input is no longer a problem

```python
import math

root = None
for k in range(1000):                         # the worst case for a plain BST
    root = avl_insert(root, k)
print("AVL height after 1000 sorted insertions:", height(root))
print("plain BST height for the same input   :", height(build_bst(list(range(500)))), "(for 500 keys)")
print("AVL height bound 1.44*log2(n+2)       :", round(1.44 * math.log2(1002), 1))
```
```text
AVL height after 1000 sorted insertions: 10
plain BST height for the same input   : 500 (for 500 keys)
AVL height bound 1.44*log2(n+2)       : 14.4
```

An AVL tree with `n` nodes has height at most about `1.44 log2(n + 2)`, at most 44% above the ideal. And each insertion needs at most one single or double rotation. Now a proper differential test: random insertions, every property checked.

```python
def heights_correct(node):
    if node is None:
        return True
    return (node.height == 1 + max(h(node.left), h(node.right))
            and heights_correct(node.left) and heights_correct(node.right))
```

```python
import math

rng = random.Random(43)
ok = True
for trial in range(200):
    n = rng.randint(0, 60)
    keys = [rng.randint(0, 80) for _ in range(n)]
    root = None
    for k in keys:
        root = avl_insert(root, k)
    out = []
    inorder(root, out)
    ok &= out == sorted(set(keys))                       # contents, and the BST order
    ok &= is_valid_bst(root)                             # the BST rule
    ok &= balanced_fast(root, [0])                       # the AVL rule at every node
    ok &= heights_correct(root)                          # stored heights are right
    ok &= height(root) <= 1.44 * math.log2(len(out) + 2) + 1
print("200 random insertion sequences: contents, BST rule, balance and heights all correct:", bool(ok))
```
```text
200 random insertion sequences: contents, BST rule, balance and heights all correct: True
```

Deletion in an AVL tree works like the BST deletion of section 9, followed by the same `rebalance` on every node of the path back up. It may need more than one rotation, up to `O(log n)`.

### Red-black trees (an overview)

A **red-black tree** is another self-balancing BST. Each node is coloured red or black, and these rules hold:

1. The root is black.
2. A red node never has a red child.
3. Every path from a node down to any empty child has the **same number of black nodes**.

Rule 3 with rule 2 forces the longest path to be at most twice the shortest, so the height is at most `2 log2(n + 1)`. After an insertion or deletion, the tree is repaired with recolouring and a few rotations (at most 2 rotations for an insertion and 3 for a deletion).

### AVL or red-black?

| | AVL | Red-black |
|---|---|---|
| Height bound | about `1.44 log2 n` | about `2 log2 n` |
| Lookup | slightly faster (more strictly balanced) | slightly slower |
| Insert / delete | more rotations | fewer rotations |
| Typical use | read-heavy data | general-purpose maps: C++ `std::map`, Java `TreeMap`, parts of the Linux kernel |

Both guarantee `O(log n)` for search, insert and delete. The choice is a matter of tuning, not of correctness.

### Other balanced structures, in one line each

- **B-trees and B+ trees:** each node holds *many* keys (hundreds), so the tree is very wide and very short. Used by databases and file systems, where each node is one disk block.
- **Treaps:** a BST on keys that is also a heap on random priorities; the randomness balances it on average.
- **Skip lists:** layers of linked lists (dsa.09) with random "express lanes"; the same expected `O(log n)` with no rotations.
- **Splay trees:** every access moves the node to the root by rotations; frequently used items stay near the top.

### What do you use in Python?

Python has no built-in balanced tree. In practice:

- For **lookup by key**, use a `dict` (average `O(1)`).
- For a **sorted collection that changes rarely**, keep a sorted `list` and use `bisect` (dsa.06): search `O(log n)`, insert `O(n)` for the shift, but the shift is fast machine code, so it is fine up to roughly a hundred thousand items.
- For a **sorted collection that changes a lot**, the third-party package `sortedcontainers` (not part of the standard library, and not used in this course) provides `SortedList`.
- For **repeatedly taking the smallest or largest**, use a heap (`heapq`, next module).

Writing a balanced tree yourself is an interview exercise and a good way to learn rotations, not something you will do at work.

**Predict the output 8.** What does the AVL tree look like (level-order list) after inserting `10, 20, 30, 40, 50, 25` in this order?

<details><summary>Answer</summary>

```python
root = None
for k in (10, 20, 30, 40, 50, 25):
    root = avl_insert(root, k)
print(to_level_list(root))
```
```text
[30, 20, 40, 10, 25, None, 50]
```

Follow it: `10, 20, 30` triggers a left rotation and gives `20` with children `10, 30`. Inserting `40` and `50` triggers another left rotation on `30`, giving `40` with children `30, 50`, still under `20`. Then `25` goes under `30` as its left child, which makes `20` right-heavy by 2; the right child `40` is left-heavy, so this is the right-left case: a right rotation on `40`, then a left rotation on `20`. The root becomes `30`. A plain BST would be a chain-like tree of height 5 here; the AVL tree has height 3.

</details>

**Try it 9.** After `rotate_right(y)`, the heights are updated for `y` first and then for `x`. What goes wrong if you update `x` first?

<details><summary>Answer</summary>

After the rotation, `y` is a child of `x`. The height of `x` depends on the height of `y`. If you compute `x` first, it uses the old (stale) height of `y`, and the stored height of `x` is wrong. The error is invisible until a later rebalance reads that height and makes a wrong decision, so the tree may become unbalanced without any crash. The test `heights_correct` above would catch it.

```python
def rotate_right_wrong(y):
    x = y.left
    y.left = x.right
    x.right = y
    update(x)                      # BUG: x is updated before y
    update(y)
    return x

root = None
for k in (3, 2, 1):
    root = avl_insert(root, k)
print(to_level_list(root), heights_correct(root))
node3 = AVLNode(3); node3.left = AVLNode(2); node3.left.left = AVLNode(1)
update(node3.left); update(node3)
wrong = rotate_right_wrong(node3)
print(to_level_list(wrong), heights_correct(wrong))
```
```text
[2, 1, 3] True
[2, 1, 3] False
```

</details>

## 15. Which technique for which problem?

Before coding, write the contract of the recursive function (section 3). The table maps common questions to the answer.

| Question about a tree | What `f(node)` returns | Style |
|---|---|---|
| number of nodes, sum, count of leaves | the number for this subtree | bottom-up |
| height, depth | the height of this subtree | bottom-up |
| is it balanced? | height, or `-1` for "unbalanced" | bottom-up with a signal |
| diameter, longest path, max path sum | the best path going down | **return** one branch, **record** the bent path |
| path sum to a leaf, all paths | (nothing, or a boolean) | top-down: pass the remaining sum or the path |
| count downward paths with a sum | (nothing) + a dictionary of prefix sums | top-down + backtracking |
| same tree, symmetric, subtree | `True` / `False` for the pair of subtrees | two nodes at once |
| lowest common ancestor | `p`, `q`, the LCA or `None` | bottom-up |
| is it a BST? | `True` / `False`, given an allowed range | top-down bounds |
| k-th smallest, sorted output | (walk) | inorder, iterative with early stop |
| per-level answers, nearest leaf, right view | levels | BFS with a queue |
| copy, save, rebuild | the new node / a string | preorder + markers, or pre/in |

Five questions to ask yourself:

1. **Is it a general tree or a BST?** If a BST, use the order to skip subtrees (`O(h)` instead of `O(n)`).
2. **Does a node's answer depend only on its subtrees (bottom-up), or on the path from the root (top-down)?** Many problems need both.
3. **Do I need a per-level result?** Then BFS.
4. **Does the value I return differ from the value I want to keep?** Then record the answer in a `nonlocal` variable.
5. **What are the base cases?** At least `None`, and often the leaf too.

## 16. Common traps, collected

1. **Calling `.val` or `.left` on `None`.** Check `if node is None` at the start of every recursive function, and `if node.left` before you go deeper by hand.
2. **Only the `None` base case when the leaf matters.** `has_path_sum`, `count_leaves`, `min_depth` need to treat a node with **no children** specially; a node with one child is not a leaf.
3. **Height conventions.** Edges or nodes, empty tree 0 or -1? Read the statement; a wrong convention is off by one everywhere.
4. **Checking a BST by comparing each node only with its children.** Pass the lower and upper bounds down, or check that the inorder is strictly increasing.
5. **Forgetting to reattach the child** in recursive `insert` and `delete`: write `root.left = insert(root.left, key)`, not just `insert(root.left, key)`.
6. **Deleting a node with two children without removing the successor.** The value would then appear twice.
7. **Storing a reference to the path** instead of a copy in "all paths" problems (`result.append(path[:])`).
8. **Wrong choice for what to return and what to record** in diameter and maximum-path-sum problems. The parent can extend only **one** branch; the answer may use two.
9. **Using `float("-inf")` or `0` as the initial best** when values can be negative. A tree of one negative node needs the answer to be that node.
10. **Recursion on a skewed tree.** A tree of 5,000 nodes in a chain exceeds Python's recursion limit. Use an explicit stack (section 5), or reduce the problem.
11. **Visiting order of the iterative versions.** Push the **right** child first to visit the left child first. Test against the recursive version.
12. **Level-order loops that do not freeze the size.** Use `for _ in range(len(queue))` to process exactly one level.
13. **Assuming the nodes exist** in LCA code. If one of `p`, `q` is missing, the simple algorithm returns the other. Check, or return a flag.
14. **Duplicates in a BST** without a rule. Decide where equal keys go (or reject them) and keep the rule everywhere.
15. **Using `==` to compare nodes** when you mean identity. Use `is` for nodes and `==` for values.
16. **Hidden shared nodes.** If two parents point to the same node, you have a graph, not a tree, and traversals will visit it twice.
17. **Forgetting that sorted insertions ruin a plain BST.** If the order of the data is not random, balance the tree or use `bisect`.

## 17. Summary

- A **tree** is a root with children, no cycles. In a **binary tree** each node has a left and a right child. Terms: parent, child, leaf, subtree, depth, height (count nodes or edges: check which), level. The height decides the speed: between `log n` and `n`.
- A tree is a **recursive** structure, so most problems are solved by one sentence: *"`f(node)` returns ... for the tree at `node`"*, plus the base case `f(None)`, plus how to combine `f(left)`, `f(right)` and `node.val`. Such a function costs `O(n)` and has the recursion depth of the tree height.
- Information goes **up** (return values: size, height) or **down** (parameters: depth, remaining sum, bounds). Hard problems use both, or **return one thing and record another** (diameter, maximum path sum).
- **Traversals:** preorder (node, left, right), inorder (left, node, right), postorder (left, right, node) are depth-first. Level order is breadth-first with a queue. Iterative versions use a stack: preorder pushes the right child first; inorder goes left as far as possible; postorder is a reversed modified preorder, or the `(node, done)` template.
- A **BST** keeps smaller values on the left and larger on the right, for whole subtrees. Search, insert, delete, min, max, successor, floor, ceiling and range queries cost `O(h)`. Inorder gives the sorted order. Validate it with bounds or an increasing inorder. Delete has three cases (leaf, one child, two children: use the inorder successor).
- **LCA:** `lca(node, p, q)` returns `p`, `q`, or the split point. In a BST, walk down by comparing values. With parent pointers it is the intersection of two linked lists.
- **Construction:** preorder + inorder, or postorder + inorder, rebuild a tree (use a dictionary for the root's index). A BST needs only its preorder. Serialise with preorder and `#` markers. A sorted list becomes a balanced BST by choosing the middle.
- A plain BST degrades to a chain on sorted input. **Balanced trees** fix this with rotations: AVL (heights differ by at most 1, height `<= 1.44 log2 n`) and red-black (colour rules, height `<= 2 log2 n`). B-trees serve databases. In Python use `dict`, `bisect`, or a heap.
- Other storage: lists of children (n-ary trees, file systems), parent arrays, and the array layout of a complete tree (children at `2i + 1` and `2i + 2`), used by heaps.

### Self-check

- [ ] I can write `size`, `height`, `invert` and `count_leaves` by stating first what the function returns.
- [ ] I can write the three recursive traversals and the three iterative ones from memory.
- [ ] I can write a level-order traversal that separates the levels.
- [ ] I can compute the diameter and the maximum path sum, and explain why they return one value and record another.
- [ ] I can write BST search, insert and delete (all three cases) and explain the successor.
- [ ] I can validate a BST correctly and give a tree that fools the "check the children" version.
- [ ] I can find the lowest common ancestor in a general tree and in a BST.
- [ ] I can rebuild a tree from preorder and inorder, and serialise and deserialise a tree.
- [ ] I can explain what a rotation does and why sorted input needs a balanced tree.
- [ ] I know when a problem needs DFS, BFS, or the BST property.

### How to practise

Do the problems in the order of the chapter: node and recursion basics first (size, height, sum), then the traversals (recursive, then iterative), then level order, then the BST operations, then paths, diameter and LCA, then construction and serialisation, and at the end the design problems (BST iterator, balanced insertion). **For every problem, write the sentence "`f(node)` returns ..." before you write any code.** Draw a small tree (including the shapes with one child and with no children) and trace your function on it. Check each solution against a brute force or against an alternative implementation on random small trees, as in this chapter. The site problems for this module (LeetCode, CSES, Codeforces) will be listed for you in the module's external list.

### Further reading

- Thomas Cormen, Charles Leiserson, Ronald Rivest and Clifford Stein, *Introduction to Algorithms*, chapters on binary search trees and red-black trees.
- Robert Sedgewick and Kevin Wayne, *Algorithms*, chapter 3.2 (binary search trees) and 3.3 (balanced search trees, including left-leaning red-black trees).
- Donald Knuth, *The Art of Computer Programming*, volume 3, section 6.2.2 ("Binary Tree Searching") and 6.2.3 ("Balanced Trees").
- J. M. Morris, "Traversing binary trees simply and cheaply" (1979): the `O(1)`-space inorder traversal mentioned in section 5.
- G. M. Adelson-Velsky and E. M. Landis, "An algorithm for the organization of information" (1962): the original AVL paper.
- The Python documentation of the `bisect` module and the `collections.deque` class.
- The "Binary Search Tree" and "AVL Tree" animations on visualgo.net, to watch insertions and rotations step by step.

Next module: **dsa.11 Heaps and priority queues**.
