## Approach

The question has two dimensions: a **position** range `[l, r)` and a **value** threshold `x`. Offline, turn one of them into time (chapter section 17): process the questions in increasing `x`, and keep a Fenwick tree over positions in which exactly the marks `< x` have been inserted. Then the answer is a plain range count.

```python
class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        i += 1
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total


def count_below(a, queries):
    n = len(a)
    order = sorted(range(n), key=lambda i: a[i])           # positions by mark
    bit = Fenwick(n)                                        # 1 at every inserted position
    answers = [0] * len(queries)
    j = 0
    for qi in sorted(range(len(queries)), key=lambda i: queries[i][2]):
        l, r, x = queries[qi]
        while j < n and a[order[j]] < x:                    # insert every mark < x
            bit.add(order[j], 1)
            j += 1
        answers[qi] = bit.prefix(r) - bit.prefix(l)
    return answers
```

The pointer `j` only moves forward, so every mark is inserted once. The strict `<` makes ties right: a mark equal to `x` is inserted only when a later, larger `x` comes.

## Complexity

Sorting `O(n log n + q log q)`, `n` insertions and `2q` prefix queries of `O(log n)`: `O((n + q) log n)` in total, `O(n + q)` memory.

## Another way

**Merge sort tree** (online, no reordering): a segment tree whose every node stores the **sorted** list of its range. A question covers `[l, r)` with `O(log n)` nodes and counts in each with `bisect_left(node_list, x)`: `O(log**2 n)` per question, `O(n log n)` memory. It also answers questions that arrive one by one. With `sorted(a[lo:hi])` per node the build is `O(n log**2 n)`; merging the children's lists makes it `O(n log n)`.
