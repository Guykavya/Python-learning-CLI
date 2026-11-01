from collections import Counter, defaultdict, deque
from functools import cache
from itertools import chain, groupby


def word_counts(text):
    return Counter(text.lower().split())


def top_words(text, n):
    return word_counts(text).most_common(n)


def group_by_length(words):
    groups = defaultdict(list)
    for w in words:
        groups[len(w)].append(w)
    return dict(groups)


def bfs_order(graph, start):
    order = []
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return order


def run_lengths(items):
    return [(key, len(list(group))) for key, group in groupby(items)]


def join_all(*lists):
    return list(chain(*lists))


@cache
def count_paths(n):
    if n <= 1:
        return 1
    return count_paths(n - 1) + count_paths(n - 2)
