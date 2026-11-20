## Hint 1

First make `search(word)` false: walk to the word's node and clear `is_end`. If the walk breaks, or `is_end` was already false, return `False`.

## Hint 2

Then free nodes. A node can go only if it has **no children** and is **not the end of another word**. Removing it can make its parent useless too, so look upward. Remember the path on the way down as a list of `(parent, letter)` pairs.

## Hint 3

```
path = []
node = root
for ch in word:
    if ch not in node.children: return False
    path.append((node, ch)); node = node.children[ch]
if not node.is_end: return False
node.is_end = False
for parent, ch in reversed(path):           # bottom up
    child = parent.children[ch]
    if child.children or child.is_end: break   # still needed
    del parent.children[ch]
return True
```
