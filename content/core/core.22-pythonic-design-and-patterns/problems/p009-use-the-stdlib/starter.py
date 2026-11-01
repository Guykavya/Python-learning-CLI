def word_counts(text):
    """{word: how many times}, ignoring case. Words are text.lower().split()."""
    counts = {}
    for w in text.lower().split():
        if w in counts:
            counts[w] = counts[w] + 1
        else:
            counts[w] = 1
    return counts


def top_words(text, n):
    """The n most common words as (word, count) pairs, most common first.
    Ties keep the order in which the words first appear."""
    counts = word_counts(text)
    pairs = sorted(counts.items(), key=lambda kv: -kv[1])
    return pairs[:n]


def group_by_length(words):
    """{length: [words of that length, in input order]}."""
    groups = {}
    for w in words:
        if len(w) not in groups:
            groups[len(w)] = []
        groups[len(w)].append(w)
    return groups


def bfs_order(graph, start):
    """Visit order of a breadth-first search. graph = {node: [neighbours]}."""
    order = []
    seen = [start]
    queue = [start]
    while queue:
        node = queue.pop(0)
        order.append(node)
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.append(nxt)
                queue.append(nxt)
    return order


def run_lengths(items):
    """'aaabcc' -> [('a', 3), ('b', 1), ('c', 2)]."""
    result = []
    for item in items:
        if result and result[-1][0] == item:
            result[-1] = (item, result[-1][1] + 1)
        else:
            result.append((item, 1))
    return result


def join_all(*lists):
    """One list with the items of all the lists, in order."""
    result = []
    for lst in lists:
        for x in lst:
            result.append(x)
    return result


def count_paths(n):
    """Ways to climb n stairs taking 1 or 2 steps at a time."""
    if n <= 1:
        return 1
    return count_paths(n - 1) + count_paths(n - 2)
