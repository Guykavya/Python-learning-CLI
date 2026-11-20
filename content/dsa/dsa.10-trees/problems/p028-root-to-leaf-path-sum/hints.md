## Hint 1

Finish the sentence: "`has_path_sum(node, target)` is true if some path from `node` down to a leaf has the sum `target`". If you take the node's value off the target, what is the same question for each child?

## Hint 2

Subtract `node.val` and ask both children with the smaller target: the answer is `True` if either side says `True`. The path may only end at a **leaf**, so the check for the value must happen at a leaf, where both children are `None`.

## Hint 3

```
if root is None: return False
if root.left is None and root.right is None:
    return root.val == target
rest = target - root.val
return has_path_sum(root.left, rest) or has_path_sum(root.right, rest)
```
