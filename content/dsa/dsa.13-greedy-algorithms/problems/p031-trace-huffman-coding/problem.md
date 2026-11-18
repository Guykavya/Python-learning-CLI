# Trace Huffman coding

This is the Huffman implementation of chapter section 13, with one change: the loop **prints** every join. Heap entries are `(weight, tie, tree)`. The tie numbers are given to the letters in **alphabetical** order (0, 1, 2, ...), and every new joined tree gets the next number. When two entries have the same weight, the **smaller tie number** comes out of the heap first.

Several weights in this table are equal, so the tie numbers decide which trees are joined. Predict **exactly** what the program prints. Do not run it.

```python
import heapq


def name(tree):
    """The letters of a tree, read from left to right."""
    if isinstance(tree, str):
        return tree
    return name(tree[0]) + name(tree[1])


def huffman_tree(freq):
    heap = []
    tie = 0
    for letter in sorted(freq):
        heap.append((freq[letter], tie, letter))
        tie += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        w1, k1, t1 = heapq.heappop(heap)
        w2, k2, t2 = heapq.heappop(heap)
        print(f"join {name(t1)}({w1}, tie {k1}) + {name(t2)}({w2}, tie {k2}) -> {w1 + w2}, tie {tie}")
        heapq.heappush(heap, (w1 + w2, tie, (t1, t2)))
        tie += 1
    return heap[0][2]


def huffman_codes(freq):
    if len(freq) == 1:
        return {next(iter(freq)): "0"}
    codes = {}

    def walk(tree, prefix):
        if isinstance(tree, str):
            codes[tree] = prefix
        else:
            walk(tree[0], prefix + "0")
            walk(tree[1], prefix + "1")

    walk(huffman_tree(freq), "")
    return codes


freq = {"r": 2, "e": 3, "d": 1, "c": 2, "b": 1, "a": 3}
codes = huffman_codes(freq)
for letter in sorted(codes):
    print(letter, codes[letter])
print("cost:", sum(freq[x] * len(codes[x]) for x in freq))
```

Write your answer in `answer.txt`, one printed line per line: the `join` lines first, then one line per letter in alphabetical order, then the `cost` line.

## How to work

1. Write the six heap entries `(weight, tie, letter)`. The tie numbers follow `sorted(freq)`, **not** the order of the dictionary as written.
2. Each round, find the **two smallest** entries: smallest weight first; on equal weight, smallest tie number first. The first one popped becomes the **left** child (`t1`), the second the **right** child (`t2`).
3. Push the joined tree with the sum of the weights and the next tie number. Keep a list of all entries still in the heap.
4. When one tree is left, draw it. Left edges are `0`, right edges are `1`; a letter's code is the path from the root.

## After you answer

1. In round 2 three entries have weight 2. Which two are joined, and why not the tree `bd`?
2. Two letters have weight 3. Which one is joined first, and what decides it?
3. Does the cost depend on the tie rule? Would the codes?
