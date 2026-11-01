## Approach

Match each hand-made loop to the tool that was built for it:

- `Counter` is a dict that counts. `most_common(n)` sorts by count and, because the sort is stable,
  keeps first-seen order for ties, which is the same order the old code gave.
- `defaultdict(list)` creates the empty list the first time a key is used.
- `list.pop(0)` shifts every remaining item, O(n) per pop. `deque.popleft()` is O(1). The `seen`
  list also becomes a set (O(1) membership instead of O(n)).
- `groupby` groups **consecutive** equal items. That is exactly a run; do not sort first.
- `chain(*lists)` walks the lists one after another without building copies.
- `@cache` stores results by argument, so `count_paths(30)` makes 31 calls instead of 2.7 million.

## Code

```python
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
```

## Complexity

`word_counts` O(n); `top_words` O(n + k log k) for k distinct words; `group_by_length` O(n);
`bfs_order` O(V + E) (the old version was O(V^2) because of the list); `run_lengths`, `join_all`
O(n); `count_paths` O(n) time and memory instead of exponential time.

## Another way

`count_paths` can be a loop with two variables (`a, b = b, a + b`), which needs no cache and no
recursion depth. `run_lengths` can use `Counter` only if order does not matter (it does here).
`group_by_length` could sort the words by length and use `groupby`, but that loses the input order of
ties unless the sort is stable (it is, so it works too).
