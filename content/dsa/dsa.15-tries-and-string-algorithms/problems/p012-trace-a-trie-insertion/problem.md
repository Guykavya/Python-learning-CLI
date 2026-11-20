# Trace a trie insertion

A trie with counts on the nodes (chapter sections 3 and 5). Predict **exactly** what this program prints. Do not run it.

```python
class Node:
    def __init__(self):
        self.children = {}
        self.pass_count = 0
        self.end_count = 0

root = Node()
nodes = 1
for word in ["tea", "ten", "te", "tea"]:
    new = 0
    node = root
    for ch in word:
        if ch not in node.children:
            node.children[ch] = Node()
            new += 1
        node = node.children[ch]
        node.pass_count += 1
    node.end_count += 1
    nodes += new
    print(f"insert {word}: new {new}, nodes {nodes}")
for p in ["t", "te", "tea", "ten"]:
    node = root
    for ch in p:
        node = node.children[ch]
    print(p, node.pass_count, node.end_count)
```

Write your answer in `answer.txt`, one printed line per line: four `insert` lines, then four count lines.

## How to work

1. Draw the root. For each word, walk its letters from the root. Draw a new node only where the letter is missing, and count those new nodes.
2. On every node you step **into** (not the root), add 1 to its pass count. On the node of the last letter, add 1 to its end count. Write both numbers next to each node.
3. For the last four lines, find the node of each prefix and read its two numbers.

## After you answer

1. Why does inserting `te` create no node, although `te` was never inserted before?
2. `te` has pass count 4 but `tea` only 2. Which words pass through `te` and not through `tea`?
3. What would `count_prefix("t")` of p003 return here, and which number is it?
