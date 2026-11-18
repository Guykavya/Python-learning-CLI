## Approach

Build the Huffman tree exactly as in chapter section 13 (min-heap of `(weight, tie, tree)`, letters numbered in sorted order, every new tree gets the next tie number), then walk it and record the depth of each leaf. The single-letter case gets length 1.

```python
import heapq


def huffman_tree(freq):
    heap = []
    tie = 0
    for letter in sorted(freq):
        heap.append((freq[letter], tie, letter))
        tie += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        w1, _, t1 = heapq.heappop(heap)
        w2, _, t2 = heapq.heappop(heap)
        heapq.heappush(heap, (w1 + w2, tie, (t1, t2)))
        tie += 1
    return heap[0][2]


def code_lengths(freq):
    if len(freq) == 1:
        return {next(iter(freq)): 1}           # a lone letter still needs one bit
    lengths = {}
    stack = [(huffman_tree(freq), 0)]          # (subtree, depth); no recursion needed
    while stack:
        tree, depth = stack.pop()
        if isinstance(tree, str):
            lengths[tree] = depth
        else:
            stack.append((tree[0], depth + 1))
            stack.append((tree[1], depth + 1))
    return lengths


def total_bits(freq):
    lengths = code_lengths(freq)
    return sum(freq[x] * lengths[x] for x in freq)
```

The walk uses an explicit stack: with counts like `1, 2, 4, 8, ...` the tree is a long chain, and a recursive walk on thousands of letters could hit the recursion limit.

**Why the tests accept other lengths.** When weights tie, the heap may pop either of the equal entries first, and different choices give different trees. The chapter proves that **every** tree Huffman can build is optimal; the tie numbers only make the choice reproducible. So the tests check the two properties that every correct answer has: the lengths fit a prefix code, and the total is the minimum.

## Complexity

`k` letters: `k` pushes and `2(k - 1)` pops at `O(log k)` each, so `O(k log k)` to build; the walk is `O(k)`. Space `O(k)`.

## Another way

Carry the letters instead of the tree: each heap entry is `(weight, tie, letters)`, and a join adds 1 to the length of every letter in both parts (see hint 3). The total can also be computed with no lengths at all: it is the sum of the weights of all joins, which is the chapter's `huffman_cost` (plus the special case of one letter, which costs `freq` bits, not 0).
