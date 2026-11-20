## Hint 1

Write the sentence first: "`gain(node)` returns the best sum of a path that **starts at `node` and goes down** (it contains at least `node`)". The parent needs exactly this number, because it can only continue into one child. What is `gain(None)`? What should happen if a child's gain is negative?

## Hint 2

At a node, take `left = max(0, gain(node.left))` and `right = max(0, gain(node.right))`: a branch with a negative sum is better left out. A path that **bends** here has the sum `node.val + left + right`: **record** it in `best`. What you **return** to the parent is `node.val + max(left, right)` (only one side).

## Hint 3

```
best = -infinity                    # not 0: a tree of one negative node must answer that negative number
def gain(node):
    if node is None: return 0
    left  = max(0, gain(node.left))
    right = max(0, gain(node.right))
    best = max(best, node.val + left + right)       # record: the path may bend here
    return node.val + max(left, right)              # return: one branch only
gain(root); return best
```
