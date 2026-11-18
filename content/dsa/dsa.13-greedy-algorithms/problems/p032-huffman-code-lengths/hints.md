## Hint 1

Start from the chapter's `huffman_tree`: heap entries `(weight, tie, tree)` with a unique integer `tie`, so two trees are never compared (with `(weight, tree)` equal weights crash with a `TypeError`). Then walk the tree and record the depth of every leaf. What depth should the single-letter case give?

## Hint 2

You can skip the tree. Let each heap entry carry the **list of letters** inside it. When two entries are joined, every letter in both gets one bit deeper: add 1 to `length[x]` for each of them. The total is then `sum(freq[x] * length[x])`, or, the same number, the sum of the weights of all joins (chapter section 13).

## Hint 3

```
if one letter: return {letter: 1}
length = {x: 0 for x in freq}
heap = [(freq[x], tie, [x]) for tie, x in enumerate(sorted(freq))]; heapify
tie = len(freq)
while len(heap) > 1:
    w1, _, xs1 = pop; w2, _, xs2 = pop
    for x in xs1 + xs2: length[x] += 1
    push (w1 + w2, tie, xs1 + xs2); tie += 1
return length
```

Copying the letter lists costs extra time on very unbalanced trees; walking the chapter's tree is `O(k)` after building it. Both are fast enough here.
