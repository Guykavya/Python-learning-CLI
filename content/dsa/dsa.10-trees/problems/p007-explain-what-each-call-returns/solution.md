## Approach

Do not read the code first. Write down what each call **means** (a count, a length, a yes/no). The base case is then the answer for a tree with no nodes, and the combining line is "what do I add for this node, given the answers for the two subtrees".

## Model answer

See `answer.md`.

## What to check

- You said what each call **returns**, not only what the code does.
- You connected each base value to the meaning (0 nodes, an empty path, 0 leaves, "not a node").
- You explained why `count_leaves` needs the leaf case: the recursion only ends in `None`.
- You gave the `None` / skip rule for `max_value`.

## Another way

Try the functions on the tree `[1]` by hand, writing each call and its return value:

```text
size(1)  = 1 + size(None) + size(None) = 1 + 0 + 0 = 1
height(1) = 1 + max(0, 0) = 1
count_leaves(1): is_leaf(1) is True, so it returns 1 at once
```

Then change `count_leaves` and trace again: without the leaf case you get `count_leaves(None) + count_leaves(None) = 0 + 0 = 0`.
