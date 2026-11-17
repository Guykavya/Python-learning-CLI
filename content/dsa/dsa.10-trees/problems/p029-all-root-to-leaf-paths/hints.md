## Hint 1

Keep a list `path` of the values from the root to the current node. On entering a node, add its value. When you leave it, take its value out again, so that the next branch starts with the correct path. At which kind of node do you store a result?

## Hint 2

Only at a leaf (no left and no right child). At that moment `path` holds exactly the values from the root to the leaf: join them into a string with `"->".join(map(str, path))`. The string is a new object, so no copy problem. Do not forget `path.pop()` after both recursive calls.

## Hint 3

```
result, path = [], []
def go(node):
    if node is None: return
    path.append(node.val)
    if node.left is None and node.right is None:
        result.append("->".join(map(str, path)))
    else:
        go(node.left)
        go(node.right)
    path.pop()
go(root)
return result
```
(Without a shared list: pass the string down, `go(node, text + "->" + str(node.val))`; then nothing needs to be un-chosen.)
