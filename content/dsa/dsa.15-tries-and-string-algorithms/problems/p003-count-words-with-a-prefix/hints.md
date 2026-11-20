## Hint 1

Give every node two counters: `pass_count` (how many logged words go through this node) and `end_count` (how many end exactly here). Then `count_prefix(p)` is the `pass_count` of the node for `p`, and `count_equal(w)` the `end_count` of the node for `w`. A missing path means 0.

## Hint 2

In `insert`, add 1 to `pass_count` of **every** node on the path, the root included (every word passes through the root, which is why `count_prefix("")` is the total). After the last letter, add 1 to `end_count`.

## Hint 3

```
insert(word):
    node = root; node.pass_count += 1
    for ch in word:
        child = node.children.get(ch) or create it
        node = child; node.pass_count += 1
    node.end_count += 1
```
