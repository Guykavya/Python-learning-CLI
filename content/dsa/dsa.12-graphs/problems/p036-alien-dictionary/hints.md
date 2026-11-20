## Hint 1

What are the vertices? (All letters that appear.) Where do the edges come from? Compare neighbours only, and only their first different letter. Once you have the graph, which earlier problem gives an order of its vertices, or says that none exists?

## Hint 2

1. `letters` = the set of all letters in all words. Make `adj` and `indeg` for them.
2. For each neighbouring pair `(w1, w2)`: walk `j` along both; at the first `j` with `w1[j] != w2[j]` add the edge `w1[j] -> w2[j]` and **stop**. If no difference is found and `len(w1) > len(w2)`, return `""`.
3. Run Kahn (p031) on the letters. If not every letter is taken, return `""`; otherwise join the order.

The same edge can come from several pairs; count it each time in both `adj` and `indeg`, or use a set for both (but be consistent).

## Hint 3

```
letters = {c for w in words for c in w}
adj = {c: [] for c in letters}; indeg = {c: 0 for c in letters}
for w1, w2 in zip(words, words[1:]):
    for a, b in zip(w1, w2):
        if a != b: adj[a].append(b); indeg[b] += 1; break
    else:
        if len(w1) > len(w2): return ""
ready = deque(c for c in letters if indeg[c] == 0); order = []
... Kahn ...
return "".join(order) if len(order) == len(letters) else ""
```
