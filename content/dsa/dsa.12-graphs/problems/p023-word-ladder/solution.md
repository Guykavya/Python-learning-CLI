## Approach

BFS from `begin`, where the neighbours of a word are generated: change one position to each of the 26 letters and keep the results that are in the set of allowed words. `dist` counts words, so `begin` starts at 1.

## Code

```python
from collections import deque

LETTERS = "abcdefghijklmnopqrstuvwxyz"


def ladder_length(begin, end, words):
    allowed = set(words)
    if end not in allowed:
        return 0
    dist = {begin: 1}
    queue = deque([begin])
    while queue:
        w = queue.popleft()
        if w == end:
            return dist[w]
        for i in range(len(w)):
            for ch in LETTERS:
                if ch == w[i]:
                    continue
                nxt = w[:i] + ch + w[i + 1:]
                if nxt in allowed and nxt not in dist:
                    dist[nxt] = dist[w] + 1
                    queue.append(nxt)
    return 0
```

## Complexity

Each word is dequeued once and generates `25 * L` candidates of length `L`: `O(N * 26 * L^2)` time with slicing, `O(N * L)` memory. For 12,000 words of length 6 that is about 11 million character operations, against 72 million word comparisons (each of 6 letters) for the pairwise method.

## Another way

**Wildcard buckets:** put each word into the buckets `"*ot"`, `"h*t"`, `"ho*"`; two words are neighbours exactly when they share a bucket. **Bidirectional BFS** (search from both ends, always grow the smaller side) explores far fewer words on big lists.
