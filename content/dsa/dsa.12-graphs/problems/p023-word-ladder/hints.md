## Hint 1

The graph is never written down; you only need "the neighbours of a word" (chapter section 2, implicit graphs). A word of length `L` has at most `25 * L` one-letter changes. How do you check quickly whether such a changed word is in the list?

## Hint 2

```
allowed = set(words); if end not in allowed: return 0
dist = {begin: 1}; queue = deque([begin])
while queue:
    w = popleft; if w == end: return dist[w]
    for i in range(len(w)):
        for ch in "abcdefghijklmnopqrstuvwxyz":
            nxt = w[:i] + ch + w[i+1:]
            if nxt in allowed and nxt not in dist: dist[nxt] = dist[w] + 1; append
return 0
```
