import heapq
from collections import Counter


def top_k_frequent(words, k):
    if k <= 0:
        return []
    counts = Counter(words)
    best = heapq.nsmallest(k, counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return [word for word, _ in best]
