## Hint 1

With sentinels, every real node has a node on both sides. So "insert between `p` and `q`" and "unlink `x`" are always the same few lines. Can `append` and `appendleft` both be written as "insert after some node"? After which node does each insert?

## Hint 2

Insert `new` after `node`, using the **old** `node.next` before you overwrite it:

```
new.prev = node
new.next = node.next
node.next.prev = new
node.next = new
```

Unlink `x`: `x.prev.next = x.next`, `x.next.prev = x.prev`, then cut `x` free.

## Hint 3

`pop` is "unlink `tail.prev`" and `popleft` is "unlink `head.next`", after checking that the list is not empty (otherwise you would unlink a sentinel). Keep a size counter and update it in the two helpers.
