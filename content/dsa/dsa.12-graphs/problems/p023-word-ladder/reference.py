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
