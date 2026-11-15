## Approach

Draw the recursion tree and read three numbers from it: the root's value (sum of the leaves, each leaf is 1), the number of nodes (calls) and the longest root-to-leaf path (depth).

## Expected output

```text
value 5
calls 9
max depth 4
deepest stack [5, 4, 3, 2]
stack at the end []
```

## Why

```text
          5
       /     \
      4       3
     / \     / \
    3   2   2   1
   / \
  2   1
```

There are 5 leaves with value 1, so `f(5) = 5`. There are 9 nodes, so 9 calls: `calls(3) = 3`, `calls(4) = 1 + 3 + 1 = 5`, `calls(5) = 1 + 5 + 3 = 9`. The longest path is 5, 4, 3, 2: four calls on the stack at the same time. When `f(2)` (the leftmost leaf) runs, `f(5)`, `f(4)` and `f(3)` are waiting for the result of their first recursive call.
Every call pops what it pushed, so the stack is empty again at the end. `f(6)` makes `1 + 9 + 5 = 15` calls.
