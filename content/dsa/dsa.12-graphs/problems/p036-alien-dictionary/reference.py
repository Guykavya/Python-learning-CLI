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
