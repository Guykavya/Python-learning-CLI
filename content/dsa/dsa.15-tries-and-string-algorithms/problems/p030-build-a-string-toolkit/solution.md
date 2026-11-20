## Approach

Collect the tools of this module in one module with one shared, strict test. Three design decisions:

- **One counter answers three questions.** `pass_count` on every node, the root included, gives `count_prefix`, and `starts_with` is `count_prefix(...) > 0`, which is also right for an empty trie. `end_count` gives `search` (and counts repeats).
- **No recursion in the DFS.** `words_with_prefix` uses an explicit stack. Pushing the children in **reverse** sorted order makes the smallest one come off the stack first, and a word is recorded when its node is popped, before anything below it: so the output is sorted.
- **Shared code.** `kmp_search` calls `prefix_function`; the trie uses one `_walk`.

```python
class _Node:
    __slots__ = ("children", "pass_count", "end_count")

    def __init__(self):
        self.children = {}
        self.pass_count = 0          # words (with repeats) that go through this node
        self.end_count = 0           # words that end exactly here


class Trie:
    def __init__(self):
        self.root = _Node()

    def insert(self, word):
        node = self.root
        node.pass_count += 1
        for ch in word:
            if ch not in node.children:
                node.children[ch] = _Node()
            node = node.children[ch]
            node.pass_count += 1
        node.end_count += 1

    def _walk(self, text):
        node = self.root
        for ch in text:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.end_count > 0

    def count_prefix(self, prefix):
        node = self._walk(prefix)
        return node.pass_count if node else 0

    def starts_with(self, prefix):
        return self.count_prefix(prefix) > 0

    def words_with_prefix(self, prefix):
        node = self._walk(prefix)
        if node is None:
            return []
        out = []
        stack = [(node, prefix)]
        while stack:                                   # iterative DFS: no recursion limit
            cur, text = stack.pop()
            if cur.end_count:
                out.append(text)                       # a word before the longer words below it
            for ch in sorted(cur.children, reverse=True):
                stack.append((cur.children[ch], text + ch))   # reversed push: smallest popped first
        return out


def prefix_function(s):
    pi = [0] * len(s)
    k = 0
    for i in range(1, len(s)):
        while k > 0 and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi


def kmp_search(text, pattern):
    m = len(pattern)
    if m == 0:
        return list(range(len(text) + 1))
    pi = prefix_function(pattern)
    found, k = [], 0
    for i, ch in enumerate(text):
        while k > 0 and ch != pattern[k]:
            k = pi[k - 1]
        if ch == pattern[k]:
            k += 1
        if k == m:
            found.append(i - m + 1)
            k = pi[k - 1]
    return found


def z_function(s):
    n = len(s)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z
```

## Complexity

| Part | Time | Memory |
|---|---|---|
| `insert`, `search`, `starts_with`, `count_prefix` | `O(L)` | `O(total letters)` for the trie |
| `words_with_prefix` | `O(p + size of the subtree + output)` | `O(subtree)` stack |
| `prefix_function`, `z_function` | `O(n)` | `O(n)` |
| `kmp_search` | `O(n + m)` | `O(m)` |

## Another way

Make the test do more of the work: a **differential test** that runs every function against a slow, obviously correct version (the definition) and against each other (KMP positions equal Z positions; `pi` derived from `z` equals `pi`) on thousands of random strings over `"ab"`. That is what the shared test file does, and it is the habit to keep for any string code you write.
