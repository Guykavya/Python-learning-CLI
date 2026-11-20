## Approach

Turn the dictionary into a graph (chapter section 18): letters are vertices, and every comparison between two neighbouring words gives at most **one** edge. At the first position `j` where they differ, `w1[j]` must come before `w2[j]`; everything after `j` is free, because the order of two words is already decided by position `j`. Comparing only neighbours is enough: the order of `words[0]` and `words[2]` follows from the two neighbouring comparisons.

One special case gives no edge but a contradiction: if `w2` is a prefix of `w1` and `w1` is longer, then `w1` would have to come after `w2` in every alphabet. The answer is `""`.

The alphabet is then a topological order of the letter graph: Kahn's algorithm (chapter section 7) builds one, or proves there is a cycle by leaving letters out. Letters that appear in no edge have in-degree 0 and enter the order like any other.

```python
from collections import deque


def alien_order(words):
    letters = sorted({c for w in words for c in w})
    adj = {c: [] for c in letters}
    indeg = {c: 0 for c in letters}
    for w1, w2 in zip(words, words[1:]):
        for a, b in zip(w1, w2):
            if a != b:
                adj[a].append(b)                   # a comes before b
                indeg[b] += 1
                break                              # later letters say nothing
        else:
            if len(w1) > len(w2):
                return ""                          # "abc" before "ab": impossible
    ready = deque(c for c in letters if indeg[c] == 0)
    order = []
    while ready:
        c = ready.popleft()
        order.append(c)
        for d in adj[c]:
            indeg[d] -= 1
            if indeg[d] == 0:
                ready.append(d)
    return "".join(order) if len(order) == len(letters) else ""
```

The `for ... else` runs the `else` part only when the inner loop ended **without** `break`, that is, when no difference was found.

## Complexity

Building the graph reads every letter of every word at most once: `O(C)` for `C` letters in total. Kahn is `O(V + E)` with at most 26 vertices and `len(words) - 1` edges.

## Another way

A DFS topological sort with three colours (p032): a GREY letter reached again means a cycle. You could also compare **all** pairs of words instead of neighbours; it gives the same answer but is `O(n^2)` comparisons for nothing.
