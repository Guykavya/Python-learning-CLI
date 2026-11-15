## Hint 1

Write the two private helpers first, exactly as in problem 10: `_unlink(node)` (its neighbours point at each other) and `_push_front(node)` (insert right after the head sentinel). Then every operation is: look up in the dictionary, then call these helpers.

## Hint 2

`get`: missing key gives `-1`; otherwise unlink the node, push it to the front, return its value. `put` with an existing key: update the value, unlink, push front. `put` with a new key on a full cache: the victim is `self.tail.prev`. Unlink it and `del self.nodes[victim.key]`, then add the new node.

## Hint 3

```
put(key, value):
    if key in nodes: node.val = value; unlink(node); push_front(node); return
    if len(nodes) == capacity:
        lru = tail.prev; unlink(lru); del nodes[lru.key]
    node = CacheNode(key, value); nodes[key] = node; push_front(node)
```
