## Hint 1

The slot of a letter is `ord(ch) - ord("a")` (that is `ord(ch) - 97`). The walk is the same as in p001, with `node.next[i]` instead of `node.children[ch]`, and `None` instead of "key missing".

## Hint 2

Increase `node_count` exactly where a new `ArrayNode` is created, by one. Nowhere else.

## Hint 3

```
insert(word):
    node = root
    for ch in word:
        i = ord(ch) - 97
        if node.next[i] is None:
            node.next[i] = ArrayNode(); node_count += 1
        node = node.next[i]
    node.is_end = True
```
