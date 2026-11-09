# dsa.15 Tries and string algorithms

## 1. Why strings need their own tools

A string is "just an array of characters", so everything you learned about arrays works on it. But strings come with questions that arrays rarely ask.

- *Does any word in this dictionary start with `"pre"`?* (autocomplete, spell check)
- *Where does the pattern `"abab"` occur inside this long text?* (search box, DNA, log files)
- *Is this string made of one smaller piece repeated?* (compression, periodic data)
- *What is the longest palindrome hiding inside this text?*

Each question can be answered by brute force. Each brute-force answer is too slow once the data gets big. This module gives you five tools that remove the slowness.

| Tool | Answers | Cost |
|---|---|---|
| **Trie** | "which stored words share this prefix?" | `O(length of the word)` per operation |
| **Prefix function / KMP** | "where does a pattern occur?" | `O(n + m)` |
| **Z-function** | "how much of the front of the string matches at each position?" | `O(n)` |
| **Rabin-Karp** | "does this window equal that pattern?" using fingerprints | `O(n + m)` expected |
| **Manacher** | "what is the longest palindrome around every centre?" | `O(n)` |

### The slowness we want to remove

Let us see the problem with our own eyes. The naive way to find a pattern of length `m` in a text of length `n` is to try every start position and compare letter by letter. We will count the letter comparisons.

```python
def naive_count_compares(text, pattern):
    """Return (positions found, number of single-letter comparisons)."""
    n, m = len(text), len(pattern)
    found, compares = [], 0
    for start in range(n - m + 1):
        k = 0
        while k < m:
            compares += 1
            if text[start + k] != pattern[k]:
                break
            k += 1
        if k == m:
            found.append(start)
    return found, compares

print(naive_count_compares("abcabcabc", "cab"))
print(naive_count_compares("a" * 20, "a" * 5 + "b"))
print(naive_count_compares("a" * 200, "a" * 50 + "b"))
```
```text
([2, 5], 11)
([], 90)
([], 7650)
```

The first call is friendly: most start positions fail after one or two comparisons. The last two are not. The text is all `a`, and the pattern is a run of `a` followed by a `b`. At every start position the naive search matches almost the whole pattern, hits the `b`, and throws all that work away. For a text of length `n` and a pattern of length `m` that is about `n * m` comparisons: `O(n * m)`. With `n = 10^6` and `m = 10^3` that is a billion steps.

The tools in this module work because they **never throw away what they have learned** about the text. KMP and Z remember how much of the pattern already matched. Rabin-Karp reuses the hash of the previous window. Manacher reuses the palindromes it has already measured. A trie reuses the shared beginnings of words.

### What you can do after this module

1. **Build a trie** from scratch with dictionary nodes and with array nodes, and do `insert`, `search`, `starts_with` and `delete`.
2. **Use a trie** for autocomplete, longest common prefix, replacing words by roots, wildcard search and Word Search II.
3. **Compute the prefix function**, explain it, and use it for KMP search, counting occurrences, borders and the period of a string.
4. **Compute the Z-function** and use it for the same problems, and to compare it with the prefix function.
5. **Use Rabin-Karp** with a modulus, avoid its traps (negative numbers, collisions), use double hashing, and find repeated substrings by binary search plus hashing.
6. **Run Manacher's algorithm** for the longest palindromic substring and for counting palindromic substrings.
7. **Choose the right tool**, including when plain `str.find` or `in` is the right answer.

### What this module reuses

- **Hash maps, `dict` and `set`**, and **polynomial rolling hashes** with their collisions are in dsa.04 (hashing), sections 2, 12 and 13. We use them and add the *rolling* part.
- **Trees, recursion on nodes and depth-first search** are in dsa.10 (trees), sections 1 to 4. A trie is a tree whose edges are labelled with letters.
- **Strings and the sliding window** are in dsa.03 (arrays and strings patterns), section 6.
- **Binary search on the answer** is in dsa.06 (binary search). We use it in the repeated-substring section.

### Conventions in this chapter

- Strings are 0-indexed. `s[i:j]` has length `j - i` and does not include `s[j]`.
- `n` is the length of the text (or the string), `m` is the length of the pattern, `L` is the length of one word.
- A **prefix** of `s` is `s[:k]` for some `k` (the empty string is a prefix; `s` itself is a prefix). A **suffix** is `s[k:]`.
- A **proper** prefix is a prefix that is not the whole string. We will say this word often.

## 2. The trie: a tree of letters

### The problem: prefix questions on a list of words

You keep a dictionary of words. A user types `"ca"` and you want to show all words that start with it.

The simplest code scans the whole list.

```python
def words_with_prefix(words, prefix):
    return [w for w in words if w.startswith(prefix)]

words = ["car", "card", "care", "cat", "dog", "dot"]
print(words_with_prefix(words, "ca"))
print(words_with_prefix(words, "do"))
print(words_with_prefix(words, "x"))
```
```text
['car', 'card', 'care', 'cat']
['dog', 'dot']
[]
```

This is correct. It costs `O(N * p)` for `N` words and a prefix of length `p`, on every keystroke. A phone dictionary has 100,000 words; the user types ten letters; that is a million comparisons for each key press. We would like the cost to depend only on the **length of what was typed**, not on the number of words.

### The idea: share the beginnings

Look at `car`, `card`, `care`, `cat`. They all begin with `ca`. Storing `ca` four times wastes space, and, worse, checking it four times wastes time. So let us store each beginning **once**.

A **trie** (pronounced "try", from re*trie*val) is a tree where:

- every **edge** is labelled with one letter;
- every **node** stands for the string you read along the path from the root to it;
- some nodes are marked as the **end of a word**.

Here are the words `car`, `card`, `care`, `cat`, `dog`, `dot`. The double brackets `[ ]` mark nodes that end a word.

```text
                 (root)
                 /    \
               c/      \d
               (c)      (d)
               |         |
              a|         |o
              (ca)      (do)
              /   \       /  \
            r/     \t   g/    \t
        [car]      [cat] [dog] [dot]
         /  \
       d/    \e
   [card]   [care]
```

Three facts to hold on to.

1. **The root stands for the empty string.** It has no letter of its own.
2. **A node knows its string only through its path.** We do not need to store the string in the node.
3. **Two words share a node exactly as long as they share a prefix.** `card` and `care` share `c`, `a`, `r`, then split.

To ask "does anything start with `ca`?", walk `c`, then `a`. If both edges exist, the answer is yes, and every word below that node starts with `ca`. The walk takes 2 steps whether we store 6 words or 6 million. The cost is `O(p)` for a prefix of length `p`, independent of `N`.

### Why mark the end of a word?

Look at the picture again. `car` is a word, and `card` is a word, but `ca` is not a word even though a node exists for it. If the trie only stored paths, we could not tell "`car` was inserted" from "`car` is just on the way to `card`". So every node carries a flag: **"a word ends here"**.

This matters for the question `search("ca")`. Reaching the node is not enough; the flag must be set.

## 3. A trie with dictionary nodes

### The node

The first implementation uses a Python `dict` for the children of each node. Each key is a letter, each value is the child node.

```python
class TrieNode:
    def __init__(self):
        self.children = {}     # letter -> TrieNode
        self.is_end = False    # does a word end exactly here?

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def _walk(self, text):
        """Follow text from the root. Return the node, or None if the path breaks."""
        node = self.root
        for ch in text:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

t = Trie()
for w in ["car", "card", "care", "cat", "dog", "dot"]:
    t.insert(w)

print(t.search("car"), t.search("ca"), t.search("cards"))
print(t.starts_with("ca"), t.starts_with("cam"), t.starts_with(""))
```
```text
True False False
True False True
```

Read the three methods slowly, because the rest of the module builds on them.

- `insert` walks from the root. For each letter it **creates the child if it is missing**, then steps into it. After the last letter it sets `is_end`.
- `_walk` is the shared helper: follow the letters, and give up (`None`) the moment an edge is missing.
- `search` is `_walk` plus "and a word ends here". `starts_with` is `_walk` alone: any node at all means some word passes through.

Notice that `search("ca")` is `False` while `starts_with("ca")` is `True`. That one difference is the whole reason for `is_end`.

### Complexity

For a word of length `L`:

| Operation | Time | Why |
|---|---|---|
| `insert` | `O(L)` | one dict lookup per letter |
| `search` | `O(L)` | one dict lookup per letter |
| `starts_with` | `O(L)` | the same walk |

The cost depends on the **word's length**, never on how many words are stored. Memory is `O(total letters)` in the worst case (no sharing at all), and less when words share prefixes.

### Hand trace: inserting step by step

Let us watch `insert` create nodes. We insert `car`, then `cat`, then `ca`, and count the nodes after each.

```python
def count_nodes(node):
    return 1 + sum(count_nodes(child) for child in node.children.values())

t = Trie()
for w in ["car", "cat", "ca", "car"]:
    before = count_nodes(t.root)
    t.insert(w)
    after = count_nodes(t.root)
    print(f"insert {w!r:6} nodes {before} -> {after}  (new nodes: {after - before})")
```
```text
insert 'car'  nodes 1 -> 4  (new nodes: 3)
insert 'cat'  nodes 4 -> 5  (new nodes: 1)
insert 'ca'   nodes 5 -> 5  (new nodes: 0)
insert 'car'  nodes 5 -> 5  (new nodes: 0)
```

Why these numbers?

1. The empty trie has one node (the root). `car` needs `c`, `a`, `r`: three new nodes.
2. `cat` walks `c`, `a` (both exist) and then needs one new node for `t`.
3. `ca` walks two existing nodes and only sets `is_end` on the node `a`. No new node.
4. Inserting `car` again changes nothing. Inserting a word twice is harmless.

### Try it: predict the output

What do these print? Think first.

```python
t = Trie()
t.insert("to")
t.insert("tea")
print(t.search("t"), t.search("to"), t.search("tea"), t.search("team"))
print(t.starts_with("te"), t.starts_with("tx"))
```
```text
False True True False
True False
```

<details><summary>Answer</summary>

The output is exactly the block above: `False True True False`, then `True False`.

- `"t"` is on the path of both words but no word ends there, so `search` is `False`.
- `"to"` and `"tea"` were inserted, so both are `True`.
- `"team"` goes one step past `tea`: there is no `m` edge, so `_walk` returns `None`.
- `"te"` is a real prefix (of `tea`), `"tx"` is not.

</details>

### The empty string and other edge cases

- `insert("")` marks the **root** as a word end. Then `search("")` is `True`. Decide whether your problem allows empty words; most do not, and some problem statements say so.
- Letters outside `a` to `z` work fine with a dict (capital letters, digits, spaces). They break the array version of section 4.
- A trie is **case sensitive** if you feed it raw strings. `"Car"` and `"car"` are different paths. Lower-case first if the problem says so.

```python
t = Trie()
t.insert("")
print(t.search(""), t.search("a"))
t.insert("Car")
print(t.search("car"), t.search("Car"))
```
```text
True False
False True
```

The empty word is stored on the root, and `Car` is not `car`.

### Where does the memory go?

Each `TrieNode` holds a dict and a boolean. An empty Python dict already costs a few dozen bytes, and an object costs more on top. A trie of one million letters can easily use more than 100 MB if there is no sharing. Compare that with the raw text, which is 1 MB. This is the main price of a trie, and it is why section 4 shows a compact version, and why section 17 asks when a trie is **not** the right tool.

## 4. A trie with array nodes

### Why another version?

A dict per node is flexible but heavy. If we know the alphabet is only `a` to `z`, each node can hold a **list of 26 slots** instead. Slot `0` is the child for `a`, slot `1` for `b`, and so on. Looking up a child is `children[ord(ch) - ord("a")]`: a plain index, no hashing.

```python
A = 26

def idx(ch):
    return ord(ch) - ord("a")

print(idx("a"), idx("c"), idx("z"))
```
```text
0 2 25
```

### The node-as-class version

```python
class ArrayNode:
    def __init__(self):
        self.next = [None] * 26
        self.is_end = False

class ArrayTrie:
    def __init__(self):
        self.root = ArrayNode()
        self.node_count = 1

    def insert(self, word):
        node = self.root
        for ch in word:
            i = ord(ch) - 97
            if node.next[i] is None:
                node.next[i] = ArrayNode()
                self.node_count += 1
            node = node.next[i]
        node.is_end = True

    def search(self, word):
        node = self.root
        for ch in word:
            node = node.next[ord(ch) - 97]
            if node is None:
                return False
        return node.is_end

at = ArrayTrie()
for w in ["car", "card", "care", "cat", "dog", "dot"]:
    at.insert(w)
print(at.node_count, at.search("care"), at.search("ca"))
```
```text
11 True False
```

The 6 words have 20 letters in total, but only 11 nodes (including the root), because beginnings are shared. Count them on the picture in section 2: the root, `c`, `ca`, `car`, `card`, `care`, `cat`, `d`, `do`, `dog`, `dot`.

### The flat-table version (a favourite in contests)

There is an even leaner way. Do not create objects at all. Keep one big list of rows, where row `v` holds the 26 child **numbers** of node `v`, and `-1` means "no child". Node `0` is the root.

```python
class FlatTrie:
    def __init__(self):
        self.nxt = [[-1] * 26]       # row 0 is the root
        self.end = [False]

    def _new_node(self):
        self.nxt.append([-1] * 26)
        self.end.append(False)
        return len(self.nxt) - 1

    def insert(self, word):
        v = 0
        for ch in word:
            i = ord(ch) - 97
            if self.nxt[v][i] == -1:
                self.nxt[v][i] = self._new_node()
            v = self.nxt[v][i]
        self.end[v] = True

    def search(self, word):
        v = 0
        for ch in word:
            v = self.nxt[v][ord(ch) - 97]
            if v == -1:
                return False
        return self.end[v]

ft = FlatTrie()
for w in ["car", "cat", "dot"]:
    ft.insert(w)

letters = "abcdefghijklmnopqrstuvwxyz"
for v, row in enumerate(ft.nxt):
    edges = {letters[i]: to for i, to in enumerate(row) if to != -1}
    print(f"node {v}: edges {edges}  end={ft.end[v]}")
```
```text
node 0: edges {'c': 1, 'd': 5}  end=False
node 1: edges {'a': 2}  end=False
node 2: edges {'r': 3, 't': 4}  end=False
node 3: edges {}  end=True
node 4: edges {}  end=True
node 5: edges {'o': 6}  end=False
node 6: edges {'t': 7}  end=False
node 7: edges {}  end=True
```

Read that table as the trie itself. Node 0 (the root) has two edges: `c` to node 1 and `d` to node 5. Node 1 (`c`) goes by `a` to node 2. Node 2 (`ca`) splits: `r` to node 3 and `t` to node 4. Nodes 3 and 4 are word ends (`car` and `cat`). The second branch, `d`, `o`, `t`, is nodes 5, 6, 7.

Why is `dot` numbered 5 to 7 and not 4 to 6? Because `cat` was inserted first and took number 4 for its `t`. A node's number is simply "how many nodes existed before it was created". Always trust the printed table over a guess.

### Dict nodes versus array nodes

| | Dict nodes | Array nodes (26 slots) |
|---|---|---|
| Child lookup | hash lookup | list index |
| Alphabet | anything hashable | fixed, small (a to z, digits, bits) |
| Memory per node | grows with the number of children | always 26 slots, mostly `None` |
| Good when | alphabet is large or unknown; few children per node | alphabet small and nodes have many children |
| Typical use | Python solutions, words with mixed characters | contests in C++, XOR tries (alphabet of 2) |

Honest advice for Python: the dict version is usually shorter, safer and no slower. Use arrays when the alphabet is tiny (2 for bits, 10 for digits) or when you want to see the memory layout. A 26-slot node with only one child wastes 25 slots.

```python
def memory_slots(words):
    """Compare: dict entries used vs array slots reserved."""
    t = Trie()
    for w in words:
        t.insert(w)
    nodes, entries = 0, 0
    stack = [t.root]
    while stack:
        node = stack.pop()
        nodes += 1
        entries += len(node.children)
        stack.extend(node.children.values())
    return nodes, entries, nodes * 26

print(memory_slots(["car", "card", "care", "cat", "dog", "dot"]))
```
```text
(11, 10, 286)
```

The three numbers are: nodes, dict entries (always `nodes - 1`, one per edge), and array slots (26 per node). The array version reserves several times more room than it uses. For binary tries (alphabet size 2) the array version has no such waste.

## 5. Counting prefixes, and deleting from a trie

### Counts on the nodes

Often we need more than yes or no. How many inserted words start with `ca`? How many times was `car` inserted? Store two integers on each node.

- `pass_count`: how many inserted words go **through** this node (including those that end here).
- `end_count`: how many words end **exactly** here.

```python
class CountNode:
    def __init__(self):
        self.children = {}
        self.pass_count = 0
        self.end_count = 0

class CountTrie:
    def __init__(self):
        self.root = CountNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = CountNode()
            node = node.children[ch]
            node.pass_count += 1
        node.end_count += 1

    def count_words_equal(self, word):
        node = self._find(word)
        return node.end_count if node else 0

    def count_words_with_prefix(self, prefix):
        node = self._find(prefix)
        return node.pass_count if node else 0

    def _find(self, text):
        node = self.root
        for ch in text:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

ct = CountTrie()
for w in ["car", "car", "card", "care", "cat", "dog"]:
    ct.insert(w)
print(ct.count_words_equal("car"), ct.count_words_equal("ca"))
print(ct.count_words_with_prefix("car"), ct.count_words_with_prefix("ca"))
print(ct.count_words_with_prefix("z"))
```
```text
2 0
4 5
0
```

Check it by hand. Words through `car`: `car`, `car`, `card`, `care` are four. Through `ca`: those four plus `cat` is five. Notice `count_words_with_prefix` is `O(p)` for any number of stored words: that is the payoff of storing counts.

With counts we can also **erase** a word cheaply: walk the word, subtract one from every `pass_count` on the way, and subtract one from `end_count`. A node whose `pass_count` reaches 0 is now useless and can be forgotten.

### Deleting from a plain trie

Deletion has two goals.

1. **Make `search(word)` false.** Easy: clear `is_end` on the last node.
2. **Free the nodes nobody needs any more.** Harder. A node can be removed only if it has no children **and** is not the end of another word. And once a node is removed, its parent might become useless too, so we must look upward.

The cleanest way is to remember the path while walking down, then prune on the way back up.

```python
def delete(trie, word):
    """Remove word from the trie. Return True if it was there."""
    node = trie.root
    path = []                         # (parent_node, letter) pairs, top to bottom
    for ch in word:
        if ch not in node.children:
            return False              # word was never inserted
        path.append((node, ch))
        node = node.children[ch]
    if not node.is_end:
        return False                  # only a prefix of something, not a word
    node.is_end = False
    for parent, ch in reversed(path): # prune from the bottom up
        child = parent.children[ch]
        if child.children or child.is_end:
            break                     # still needed by another word
        del parent.children[ch]
    return True

t = Trie()
for w in ["car", "card", "cat"]:
    t.insert(w)
print("nodes at start:", count_nodes(t.root))
print(delete(t, "card"), "nodes:", count_nodes(t.root), "| car still there:", t.search("car"))
print(delete(t, "cat"), "nodes:", count_nodes(t.root), "| starts with 'ca':", t.starts_with("ca"))
print(delete(t, "ca"), delete(t, "dog"))
print(delete(t, "car"), "nodes:", count_nodes(t.root))
```
```text
nodes at start: 6
True nodes: 5 | car still there: True
True nodes: 4 | starts with 'ca': True
False False
True nodes: 1
```

Trace it.

- Start: `car` is 3 nodes, `card` adds `d`, `cat` adds `t`: root + `c`,`a`,`r`,`d`,`t` = 6 nodes.
- Delete `card`: the node `d` has no children and is no longer an end, so it is removed. The node `r` is still the end of `car`, so the loop stops there. 5 nodes.
- Delete `cat`: node `t` is removed. Node `a` still has the child `r`, so we stop. 4 nodes.
- `ca` is only a prefix, `dog` was never inserted: both return `False` and change nothing.
- Delete `car`: `r`, then `a`, then `c` each become childless non-ends, so all three go. Only the root remains.

The trap: the loop must go **bottom up** and must **stop** at the first node that is still needed. Going top down, or never stopping, breaks other words.

### A recursive version

Some people find the recursive version more natural: a function that returns "should my parent delete me?".

```python
def delete_rec(node, word, depth=0):
    """Return True if this node can now be removed by its parent."""
    if depth == len(word):
        if not node.is_end:
            return False                      # word not present
        node.is_end = False
        return not node.children              # removable if it has no children
    ch = word[depth]
    child = node.children.get(ch)
    if child is None:
        return False
    if delete_rec(child, word, depth + 1):
        del node.children[ch]
        return not node.is_end and not node.children
    return False

t = Trie()
for w in ["car", "card", "cat"]:
    t.insert(w)
delete_rec(t.root, "card")
delete_rec(t.root, "car")
print(t.search("car"), t.search("cat"), count_nodes(t.root))
```
```text
False True 4
```

Both versions are `O(L)` time. The iterative one uses `O(L)` extra space for the path, the recursive one uses `O(L)` call-stack space.

## 6. Autocomplete

### Listing all words below a node

To list every word that starts with a prefix, first walk to the prefix node (`O(p)`), then do a **depth-first search** below it, collecting the letters on the way (dsa.10, sections 3 and 4). Whenever a node has `is_end`, record the word built so far.

```python
def collect(node, path, out):
    """Depth-first: append every word under node to out. path is a list of letters."""
    if node.is_end:
        out.append("".join(path))
    for ch in sorted(node.children):          # sorted: alphabetical output
        path.append(ch)
        collect(node.children[ch], path, out)
        path.pop()                            # backtrack (dsa.07)

def autocomplete(trie, prefix):
    node = trie._walk(prefix)
    if node is None:
        return []
    out = []
    collect(node, list(prefix), out)
    return out

t = Trie()
for w in ["car", "card", "care", "cat", "cart", "dog", "dot", "do"]:
    t.insert(w)
print(autocomplete(t, "car"))
print(autocomplete(t, "do"))
print(autocomplete(t, "x"))
print(autocomplete(t, ""))
```
```text
['car', 'card', 'care', 'cart']
['do', 'dog', 'dot']
[]
['car', 'card', 'care', 'cart', 'cat', 'do', 'dog', 'dot']
```

The `path.append` / `path.pop` pair is the backtracking pattern from dsa.07: add a letter, explore below, remove the letter. Using a list for the path avoids building a new string at every step.

**Cost.** Walking to the prefix is `O(p)`. The DFS visits every node below it, so it costs about the **size of that subtree** plus the cost of building the output strings. You pay for the answer you ask for. If the prefix is short, the answer can be huge, so real systems return only the best few.

### Top-k suggestions by popularity

Store a **frequency** on each word end, then keep the best `k`. The simplest way: collect everything, sort by `(-frequency, word)`, and cut.

```python
class FreqNode:
    def __init__(self):
        self.children = {}
        self.freq = 0             # 0 means "no word ends here"

def insert_freq(root, word, amount=1):
    node = root
    for ch in word:
        if ch not in node.children:
            node.children[ch] = FreqNode()
        node = node.children[ch]
    node.freq += amount

def top_k(root, prefix, k):
    node = root
    for ch in prefix:
        if ch not in node.children:
            return []
        node = node.children[ch]
    found = []
    stack = [(node, prefix)]
    while stack:                               # iterative DFS: no recursion limit worries
        cur, text = stack.pop()
        if cur.freq > 0:
            found.append((-cur.freq, text))
        for ch, child in cur.children.items():
            stack.append((child, text + ch))
    found.sort()                               # most frequent first, ties alphabetical
    return [text for _, text in found[:k]]

root = FreqNode()
history = ["car"] * 5 + ["card"] * 9 + ["care"] * 5 + ["cat"] * 2 + ["dog"] * 7
for w in history:
    insert_freq(root, w)
print(top_k(root, "ca", 3))
print(top_k(root, "car", 2))
print(top_k(root, "d", 5))
```
```text
['card', 'car', 'care']
['card', 'car']
['dog']
```

`card` was typed 9 times, so it is first. `car` and `care` tie at 5, and the tuple sort breaks the tie alphabetically. A tuple `(-freq, text)` is the standard way to get "largest frequency first, then alphabetical" out of one `sort()`.

For huge subtrees, sorting everything wastes time. Two upgrades:

- keep a heap of size `k` (dsa.11, section 5) while walking: `O(S log k)` for a subtree of size `S`;
- or store the **best `k` words at every node** while inserting, so a query is just the walk, `O(p)`. This costs memory but makes lookups instant. Search engines do something like this.

### A step-by-step typing simulation

The classic "search suggestions" problem: as the user types a word one letter at a time, show up to 3 suggestions after each letter.

```python
def suggestions(words, typed, k=3):
    t = Trie()
    for w in words:
        t.insert(w)
    result = []
    for end in range(1, len(typed) + 1):
        result.append(autocomplete(t, typed[:end])[:k])
    return result

for step in suggestions(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse"):
    print(step)
```
```text
['mobile', 'moneypot', 'monitor']
['mobile', 'moneypot', 'monitor']
['mouse', 'mousepad']
['mouse', 'mousepad']
['mouse', 'mousepad']
```

Each line is the answer after one more key: `m`, `mo`, `mou`, `mous`, `mouse`. As the prefix grows the list shrinks. Because the lists are alphabetical, we cut to `k = 3` after collecting.

### Try it: autocomplete order

Which three words does `suggestions(["bat", "bar", "bark", "ball"], "ba")` give after the last key `a`, and in what order? Write your answer, then run it.

```python
print(suggestions(["bat", "bar", "bark", "ball"], "ba")[-1])
```
```text
['ball', 'bar', 'bark']
```

<details><summary>Answer</summary>

Alphabetical order of all four matches is `ball`, `bar`, `bark`, `bat`. The function cuts the first `k = 3`, so `bat` is dropped even though it was inserted first. The DFS order is decided by `sorted(node.children)`, not by insertion order.

</details>

## 7. Trie applications: common prefix, root words and wildcards

### Longest common prefix

Given several words, find the longest string that begins all of them. In a trie of those words, the common prefix is the path from the root **while the path has no choice**: the current node has exactly one child, and no word ends at it.

```python
def longest_common_prefix(words):
    if not words:
        return ""
    t = Trie()
    for w in words:
        t.insert(w)
    node, prefix = t.root, []
    while len(node.children) == 1 and not node.is_end:
        ch = next(iter(node.children))      # the only key
        prefix.append(ch)
        node = node.children[ch]
    return "".join(prefix)

print(repr(longest_common_prefix(["flower", "flow", "flight"])))
print(repr(longest_common_prefix(["dog", "racecar", "car"])))
print(repr(longest_common_prefix(["interview", "internet", "interval"])))
print(repr(longest_common_prefix(["ab", "ab"])))
print(repr(longest_common_prefix(["abc", "ab"])))
```
```text
'fl'
''
'inter'
'ab'
'ab'
```

Why do we stop when `is_end` is true? Look at the last example: `ab` ends at a node that has a child `c`. The prefix cannot grow past `ab` because the word `ab` has no next letter to share. The two stop conditions are: **a branch** (two or more children) or **a word ends here**.

A trie is overkill for this particular problem. Two cheaper ways to get the same answer:

```python
def lcp_sort(words):
    """Only the smallest and the largest word (alphabetically) can differ the most."""
    if not words:
        return ""
    lo, hi = min(words), max(words)
    i = 0
    while i < len(lo) and i < len(hi) and lo[i] == hi[i]:
        i += 1
    return lo[:i]

def lcp_scan(words):
    """Vertical scan: compare column by column."""
    if not words:
        return ""
    for i, ch in enumerate(words[0]):
        for w in words[1:]:
            if i == len(w) or w[i] != ch:
                return words[0][:i]
    return words[0]

tests = [["flower", "flow", "flight"], ["dog", "racecar", "car"], ["abc", "ab"], ["ab", "ab"]]
for words in tests:
    print(lcp_sort(words) == lcp_scan(words) == longest_common_prefix(words), repr(lcp_scan(words)))
```
```text
True 'fl'
True ''
True 'ab'
True 'ab'
```

All three agree. The vertical scan costs `O(total letters)` and needs no extra memory, so it wins for a one-off query. The trie wins when the **same word list is queried many times** with different prefixes. Choose the tool by the number of questions, not by the topic.

### Replace words (shortest root)

*A sentence and a dictionary of roots are given. Replace every word in the sentence by the shortest root that is a prefix of it. Leave words with no root alone.*

Example: roots `cat`, `bat`, `rat`; sentence `the cattle was rattled by the battery` becomes `the cat was rat by the bat`.

For each word we walk the trie and **stop at the first node where a word ends**: that is the shortest root.

```python
def replace_words(roots, sentence):
    t = Trie()
    for r in roots:
        t.insert(r)

    def shortest_root(word):
        node = t.root
        for i, ch in enumerate(word):
            if ch not in node.children:
                return word                  # no root is a prefix
            node = node.children[ch]
            if node.is_end:
                return word[:i + 1]          # first (= shortest) root found
        return word                          # word is shorter than any root

    return " ".join(shortest_root(w) for w in sentence.split())

print(replace_words(["cat", "bat", "rat"], "the cattle was rattled by the battery"))
print(replace_words(["a", "aa", "aaa"], "aadsfasf absbs bbab cadsfafs"))
print(replace_words(["ab", "abc"], "abcd ab a"))
```
```text
the cat was rat by the bat
a a bbab cadsfafs
ab ab a
```

In the second example both `a` and `aa` are roots. The word `aadsfasf` is reached first through `a`, which already ends a word, so `a` wins: **shortest wins because we stop at the first word end**. In the last example the word `a` is shorter than every root, so it is unchanged.

Time: building is `O(total letters of roots)`. Each sentence word costs at most `O(min(word length, longest root))`. The alternative, a `set` of roots with `word[:k] in roots` for each `k`, costs `O(L^2)` per word because every slice is a copy. The trie avoids those copies.

### Words with wildcards

*Design a dictionary: `add_word(word)` and `search(pattern)`, where `.` in the pattern matches any single letter.*

A normal walk breaks at `.` because we do not know which edge to follow. The answer: **try all of them**. Use recursion: at a `.`, loop over every child and succeed if any child succeeds.

```python
class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def add_word(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, pattern):
        return self._search(self.root, pattern, 0)

    def _search(self, node, pattern, i):
        if i == len(pattern):
            return node.is_end
        ch = pattern[i]
        if ch == ".":
            for child in node.children.values():
                if self._search(child, pattern, i + 1):
                    return True
            return False
        if ch not in node.children:
            return False
        return self._search(node.children[ch], pattern, i + 1)

wd = WordDictionary()
for w in ["bad", "dad", "mad", "pad"]:
    wd.add_word(w)
for q in ["pad", "bad", ".ad", "b..", "b.", "...", "..d.", "x.."]:
    print(f"{q!r:7} -> {wd.search(q)}")
```
```text
'pad'   -> True
'bad'   -> True
'.ad'   -> True
'b..'   -> True
'b.'    -> False
'...'   -> True
'..d.'  -> False
'x..'   -> False
```

Reading the output: `.ad` matches `bad`, `dad`, `mad`, `pad`. `b..` matches `bad`. `b.` is false because every stored word has 3 letters; the pattern ends one level too early, where `is_end` is false. `..d.` is false for the same reason on the other side.

**Cost.** With no dots it is `O(L)`. With `d` dots it can branch, but it can never visit more nodes than exist in the trie. A pattern of all dots on a trie of `N` nodes can touch all of them: `O(N)` worst case. That is still far better than comparing against every word when the pattern has few dots.

### Try it: how many nodes does the wildcard search visit?

Predict how many nodes `search("b..")`, `search("...")` and `search("x..")` visit on the dictionary above (count the root as one visit, and stop at the first success). Then run the counter.

```python
def visited(wd, pattern):
    count = [0]
    def go(node, i):
        count[0] += 1
        if i == len(pattern):
            return node.is_end
        ch = pattern[i]
        if ch == ".":
            children = list(node.children.values())
        elif ch in node.children:
            children = [node.children[ch]]
        else:
            children = []
        for child in children:
            if go(child, i + 1):
                return True
        return False
    go(wd.root, 0)
    return count[0]

print(visited(wd, "b.."), visited(wd, "..."), visited(wd, "x.."))
print(visited(wd, "..x"))
```
```text
4 4 1
9
```

<details><summary>Answer</summary>

`b..` visits the root, `b`, `ba`, `bad`: 4 visits, a single path. `...` follows the first child at each level and finds a word at once (it stops at the first success), so it is also 4. `x..` stops at the root because there is no `x` edge: 1 visit. The last line, `..x`, never succeeds, so it must explore every branch: the root, 4 first-level nodes and 4 second-level nodes, which is 9 visits. It never enters the third level, because no node has an `x` edge. Failing searches with many dots are the worst case. 

</details>

## 8. Word Search II: a trie guiding a depth-first search

### The problem

You get a grid of letters and a list of words. Find every word that can be built by walking from cell to neighbouring cell (up, down, left, right), using each cell at most once per word.

```text
    o  a  a  n
    e  t  a  e
    i  h  k  r
    i  f  l  v

words = oath, pea, eat, rain
```

`oath` is there: start at the `o` in the top-left corner, go right to `a`, down to `t`, down to `h`. `eat` is there too (`e`, `a`, `t`). `pea` and `rain` are not, so the answer is `oath` and `eat`.

### The slow way

For each word, run a separate depth-first search from every cell. If there are `W` words, the board has `R * C` cells and words have length `L`, that is about `W * R * C * 3^L` steps in the worst case. Most work is repeated: `oath` and `oat` and `oak` all begin by trying the same `o`, `a`.

### The fast way: search all words at once

Put all words in a trie. Run **one** depth-first search from every cell, and walk the **trie** at the same time. At each step the letter we are standing on must be a child of the current trie node. If it is not, **no word can start this way**: stop at once (prune). If the trie node is a word end, we found a word.

```python
def find_words(board, words):
    root = {}                                  # dict-of-dicts trie; "$" holds a finished word
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = w

    rows, cols = len(board), len(board[0])
    found = []
    steps = [0]

    def dfs(r, c, parent):
        steps[0] += 1
        ch = board[r][c]
        node = parent[ch]
        if "$" in node:
            found.append(node.pop("$"))        # take the word, and never report it twice
        board[r][c] = "#"                      # mark the cell as used
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] in node:
                dfs(nr, nc, node)
        board[r][c] = ch                       # restore (backtrack)
        if not node:                           # nothing left below: cut this branch away
            del parent[ch]

    for r in range(rows):
        for c in range(cols):
            if board[r][c] in root:
                dfs(r, c, root)
    return sorted(found), steps[0]

board = [list("oaan"), list("etae"), list("ihkr"), list("iflv")]
print(find_words(board, ["oath", "pea", "eat", "rain"]))
```
```text
(['eat', 'oath'], 9)
```

Let us read the code, because every line matters.

1. **The trie is made of plain dicts.** `node.setdefault(ch, {})` returns the child, creating an empty dict if missing. The key `"$"` is not a letter, so it can sit beside the letter keys and store the finished word itself. Storing the whole word at the end saves rebuilding it from the path.
2. **`board[nr][nc] in node`** checks the trie before recursing: only cells whose letter continues some word are visited. This is the pruning that makes the search fast.
3. **`board[r][c] = "#"`** marks the cell as used so a path never reuses it. We restore it on the way back. This is the backtracking pattern from dsa.07.
4. **`node.pop("$")`** removes the word once found. If `eat` could be reached by two different paths, we must report it once.
5. **`if not node: del parent[ch]`** removes branches that are completely used up. After `oath` is found, the nodes `o`, `a`, `t`, `h` hold nothing, so they are deleted and never explored again. This keeps long boards fast when most words are already found.

A cell can only be used once per path, but the *same cell* may be used by different words: after we restore it, other paths can step on it.

### The effect of the trie

Compare the number of recursive calls with and without the trie.

```python
def find_one_word(board, word):
    rows, cols = len(board), len(board[0])
    steps = [0]
    def dfs(r, c, k):
        steps[0] += 1
        if board[r][c] != word[k]:
            return False
        if k == len(word) - 1:
            return True
        ch = board[r][c]
        board[r][c] = "#"
        ok = False
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dfs(nr, nc, k + 1):
                ok = True
                break
        board[r][c] = ch
        return ok
    hit = any(dfs(r, c, 0) for r in range(rows) for c in range(cols))
    return hit, steps[0]

words = ["oath", "pea", "eat", "rain"]
total = 0
for w in words:
    hit, s = find_one_word(board, w)
    total += s
    print(f"{w:5} found={hit!s:5} steps={s}")
print("one search per word: total steps =", total)
print("one search with trie: total steps =", find_words(board, words)[1])
```
```text
oath  found=True  steps=5
pea   found=False steps=16
eat   found=True  steps=18
rain  found=False steps=19
one search per word: total steps = 58
one search with trie: total steps = 9
```

The trie version makes far fewer calls (the exact counts are in the output above). Note that the failing words `pea` and `rain` cost the separate searches a lot, because each one must try every start cell before giving up, while the trie stops a branch the moment no word continues. The gap grows with the **number of words**: with thousands of words the separate-search approach repeats the same prefix over and over, and the trie shares it.

### Complexity

Let `R * C` be the number of cells and `L` the longest word. One DFS can go at most `L` deep and has at most 3 choices after the first step (not back where it came from). So each start cell costs `O(3^(L-1))` at worst, total `O(R * C * 3^L)`, **independent of the number of words**, because the trie prunes. Building the trie is `O(total letters)`. Extra space is `O(total letters)` for the trie plus `O(L)` for the recursion.

## 9. The XOR trie (a short look)

### The problem

*Given a list of non-negative integers, find the largest value of `a ^ b` over pairs of list items.* (`^` is XOR, from dsa.02.)

Brute force tries every pair: `O(n^2)`. A trie over the **bits** of the numbers does it in `O(n * B)`, where `B` is the number of bits (32 is typical).

### The idea

Write every number as a fixed-length string of bits, highest bit first. Insert it in a trie with only two children per node: `0` and `1`.

To maximise `x ^ y` for a given `x`, we want `y` to differ from `x` on the **highest** bit if possible, because a high bit is worth more than all the lower bits together. So walk down the trie, and at each bit **prefer the child that is the opposite of `x`'s bit**. If that child does not exist, take the other one.

```python
def max_xor_pair(nums, bits=8):
    root = {}
    def insert(x):
        node = root
        for b in range(bits - 1, -1, -1):
            bit = (x >> b) & 1
            node = node.setdefault(bit, {})

    def best_partner(x):
        node, value = root, 0
        for b in range(bits - 1, -1, -1):
            bit = (x >> b) & 1
            want = 1 - bit                       # the opposite bit
            if want in node:
                value |= (1 << b)                # XOR gets a 1 here
                node = node[want]
            else:
                node = node[bit]                 # forced to match, XOR gets 0
        return value

    best = 0
    insert(nums[0])
    for x in nums[1:]:
        best = max(best, best_partner(x))
        insert(x)
    return best

nums = [3, 10, 5, 25, 2, 8]
print(max_xor_pair(nums))

best = max(a ^ b for a in nums for b in nums)
print("brute force:", best)
print(f"{5:05b} ^ {25:05b} = {5 ^ 25:05b}")
```
```text
28
brute force: 28
00101 ^ 11001 = 11100
```

The best pair is `5` and `25`: `00101` against `11001` differ on every bit but one, giving `11100`, which is 28. The bit values are 8 bits wide in the code (`bits=8`), which is enough for numbers below 256; use `bits=32` for ordinary 32-bit numbers.

### Why greedy per bit is correct

A 1 in bit position `b` is worth `2^b`, which is **more than all lower bits together** (`2^b > 2^(b-1) + ... + 1`). So at every level, getting a 1 in the current bit beats anything that can happen below. That is a greedy argument, in the spirit of dsa.13.

### Complexity

Insert and query are `O(B)` each, so the whole job is `O(n * B)` time and `O(n * B)` space. For 32-bit numbers `B` is a constant, so this is effectively linear. The same idea answers "max XOR with a given number", "max XOR subarray" (with prefix XORs, dsa.03) and offline queries.

## 10. The prefix function: what a failed match still teaches

### The idea in one picture

Back to the slow search from section 1. Suppose we search for `abcabd` and the text reads `abcabcabd`. We match `abcab`, then the text has `c` where the pattern wants `d`.

```text
text:    a b c a b c a b d
pattern: a b c a b d
                     ^ mismatch (c versus d)
```

The naive search shifts the pattern by one and starts from scratch. But we already **know** the last five text letters: `abcab`. Does a shorter piece of the pattern match the end of what we just read? Yes: `ab` is both the **beginning** of the pattern and the **end** of `abcab`. So we can continue as if `ab` were already matched, and compare the text's `c` against the pattern's third letter `c`. No letter of the text is read twice.

All we needed was a table that says: *for each prefix of the pattern, what is the longest shorter piece that is both its beginning and its end?* That table is the **prefix function**.

### Definitions

A **border** of a string `t` is a **proper** prefix of `t` that is also a suffix of `t`. For `t = "abcab"` the borders are `"ab"` (and the empty string). The word `abcab` itself is not a border (it is not proper).

The **prefix function** of `s` is an array `pi` of the same length where

> `pi[i]` = the length of the longest border of the prefix `s[0..i]`.

Equivalently: the longest proper prefix of `s[:i+1]` that equals a suffix of `s[:i+1]`. A direct translation of this definition gives a slow but obviously right version, which we keep as a checker.

```python
def prefix_function_slow(s):
    """Straight from the definition. O(n^3) in the worst case. Used only to check."""
    pi = []
    for i in range(len(s)):
        t = s[:i + 1]
        best = 0
        for k in range(1, len(t)):            # k < len(t): proper
            if t[:k] == t[-k:]:
                best = k
        pi.append(best)
    return pi

print(prefix_function_slow("abcabcd"))
print(prefix_function_slow("aabaaab"))
print(prefix_function_slow("aaaa"))
```
```text
[0, 0, 0, 1, 2, 3, 0]
[0, 1, 0, 1, 2, 2, 3]
[0, 1, 2, 3]
```

Read the first one: `abcabcd` gives `[0, 0, 0, 1, 2, 3, 0]`.

- `a`: no proper prefix other than empty, so 0.
- `ab`: border would need `a` = `b`; no, so 0. Same for `abc`.
- `abca`: the prefix `a` equals the suffix `a`: 1.
- `abcab`: `ab` equals `ab`: 2.
- `abcabc`: `abc` equals `abc`: 3.
- `abcabcd`: the string ends in `d`, which never appeared before: 0.

### Computing it in O(n)

The trick: **use the answer for the previous position to get the next one.** Suppose `pi[i-1] = k`. That means `s[0..k-1]` equals the `k` letters that end at `i-1`. To extend a border by one letter at position `i`, we need `s[i] == s[k]`.

- If `s[i] == s[k]`: the border grows to `k + 1`.
- If not: the border of length `k` cannot be extended. The next best candidate is the **longest border of the border**, which is `pi[k-1]`. Try again with `k = pi[k-1]`. Keep falling back until a letter matches or `k` reaches 0.

```python
def prefix_function(s):
    n = len(s)
    pi = [0] * n
    k = 0                                    # length of the current border
    for i in range(1, n):
        while k > 0 and s[i] != s[k]:
            k = pi[k - 1]                    # fall back to a shorter border
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi

for text in ["abcabcd", "aabaaab", "aaaa", "abab", "a", ""]:
    print(f"{text!r:10} {prefix_function(text)}  slow-check: {prefix_function(text) == prefix_function_slow(text)}")
```
```text
'abcabcd'  [0, 0, 0, 1, 2, 3, 0]  slow-check: True
'aabaaab'  [0, 1, 0, 1, 2, 2, 3]  slow-check: True
'aaaa'     [0, 1, 2, 3]  slow-check: True
'abab'     [0, 0, 1, 2]  slow-check: True
'a'        [0]  slow-check: True
''         []  slow-check: True
```

Notice the loop starts at `i = 1`: `pi[0]` is always 0, because a one-letter string has no proper non-empty prefix.

### Hand trace with the fallback

Let us trace the interesting string `aabaaab`. We print the border length before the letter, each fallback, and the result.

```python
def trace_prefix_function(s):
    pi = [0] * len(s)
    k = 0
    print(f"{'i':>2} {'s[i]':>4} {'k before':>8}  steps                          pi[i]")
    for i in range(1, len(s)):
        steps = []
        while k > 0 and s[i] != s[k]:
            steps.append(f"s[{i}]={s[i]} != s[{k}]={s[k]} -> k=pi[{k - 1}]={pi[k - 1]}")
            k = pi[k - 1]
        if s[i] == s[k]:
            steps.append(f"s[{i}]={s[i]} == s[{k}]={s[k]} -> k={k + 1}")
            k += 1
        else:
            steps.append(f"s[{i}]={s[i]} != s[{k}]={s[k]} -> stays 0")
        pi[i] = k
        print(f"{i:>2} {s[i]:>4} {pi[i - 1]:>8}  {'; '.join(steps):<30} {k}")
    return pi

print(trace_prefix_function("aabaaab"))
```
```text
 i s[i] k before  steps                          pi[i]
 1    a        0  s[1]=a == s[0]=a -> k=1        1
 2    b        1  s[2]=b != s[1]=a -> k=pi[0]=0; s[2]=b != s[0]=a -> stays 0 0
 3    a        0  s[3]=a == s[0]=a -> k=1        1
 4    a        1  s[4]=a == s[1]=a -> k=2        2
 5    a        2  s[5]=a != s[2]=b -> k=pi[1]=1; s[5]=a == s[1]=a -> k=2 2
 6    b        2  s[6]=b == s[2]=b -> k=3        3
[0, 1, 0, 1, 2, 2, 3]
```

Walk through three rows.

- Row `i = 3`: before it `pi[2] = 0`. The letter `a` is compared with `s[0] = a`: equal, so the border becomes 1.
- Row `i = 5`: `k` was 2 (`aa` is a border of `aabaa`). The new letter is `a` but `s[2]` is `b`: mismatch. Fall back to `pi[1] = 1` (the border of `aa` is `a`), then compare with `s[1] = a`: match, so `k` becomes 2. The border is not 3, because the letters `aab` do not end at position 5.
- Row `i = 6`: `k = 2`, the new letter `b` equals `s[2] = b`, so `k = 3`: `aab` is both the beginning and the end of `aabaaab`.

The most important picture: **a fallback is not a restart.** The fallback jumps to the longest border *of the border*, which is exactly the next candidate for a prefix that still ends at position `i - 1`.

### Why this is O(n), not O(n^2)

The `while` loop looks like it could be slow, so let us count.

- `k` goes **up by at most 1** per iteration of the outer loop (only in the `k += 1` line).
- Each step of the inner `while` makes `k` **strictly smaller** (`pi[k-1] < k`).
- `k` can never go below 0.

So over the whole run, the total number of fallbacks is at most the total number of increases, which is at most `n - 1`. Total work is `O(n)`: **amortised**. A single iteration may fall back many times, but then `k` was large because many earlier iterations increased it.

We can check this by counting.

```python
def prefix_function_counted(s):
    pi = [0] * len(s)
    k = 0
    compares = 0
    for i in range(1, len(s)):
        while k > 0:
            compares += 1
            if s[i] == s[k]:
                break
            k = pi[k - 1]
        else:
            compares += 1
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return compares

for s in ["a" * 1000, "ab" * 500, "a" * 999 + "b", "abcdefghij" * 100]:
    n = len(s)
    print(f"n={n:5}  comparisons={prefix_function_counted(s):5}  bound 2n={2 * n}")
```
```text
n= 1000  comparisons=  999  bound 2n=2000
n= 1000  comparisons=  999  bound 2n=2000
n= 1000  comparisons= 1997  bound 2n=2000
n= 1000  comparisons=  999  bound 2n=2000
```

Each count stays below `2n`, as the argument says. The input `"a" * 999 + "b"` comes closest to the limit: the last letter forces `k` to fall back through the whole chain, but that only happens once, and it can only happen because `k` was raised to 998 by 998 cheap steps before.

### Try it: compute by hand

Compute the prefix function of `ababaca` on paper, then check.

```python
print(prefix_function("ababaca"))
```
```text
[0, 0, 1, 2, 3, 0, 1]
```

<details><summary>Answer</summary>

`ababaca` gives `[0, 0, 1, 2, 3, 0, 1]`. Letter by letter: `a` is 0, `ab` is 0, `aba` has border `a` (1), `abab` has border `ab` (2), `ababa` has border `aba` (3). Then `c` is new, so `ababac` is 0. Finally `ababaca` ends with `a`, which equals the first letter, so 1.

</details>

### The two traps of the prefix function

1. **Off-by-one in the fallback.** The fallback is `k = pi[k - 1]`, with `k - 1`, not `pi[k]`. The value `k` is a **length**, and the array index of the last letter of that border is `k - 1`. Writing `pi[k]` gives a wrong answer on many inputs and an `IndexError` on others.
2. **Comparing with the wrong letter.** The letter to compare with `s[i]` is `s[k]` (the letter that would **extend** the border), not `s[k - 1]` and not `s[i - 1]`.

Here is the wrong version, so you can see how it fails.

```python
def prefix_function_wrong(s):
    pi = [0] * len(s)
    k = 0
    for i in range(1, len(s)):
        guard = 0
        while k > 0 and s[i] != s[k]:
            k = pi[k]                       # BUG: should be pi[k - 1]
            guard += 1
            if guard > 100:
                raise RuntimeError("stuck in an endless loop")
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi

for text in ["aabaaab", "abcabcd", "aaab"]:
    try:
        print(text, prefix_function_wrong(text), "correct:", prefix_function(text))
    except RuntimeError as e:
        print(text, "RuntimeError:", e, "| correct:", prefix_function(text))
```
```text
aabaaab RuntimeError: stuck in an endless loop | correct: [0, 1, 0, 1, 2, 2, 3]
abcabcd [0, 0, 0, 1, 2, 3, 0] correct: [0, 0, 0, 1, 2, 3, 0]
aaab RuntimeError: stuck in an endless loop | correct: [0, 1, 2, 0]
```

The bug is not always visible. For `abcabcd` the table happens to come out right, because no fallback is needed there. For the other two inputs the loop never ends (the guard in the code stops the loop so that the chapter can show you; without the guard your program would hang). With other inputs the wrong version returns a wrong table without any error. Wrong code that sometimes works is the most dangerous kind, so test the prefix function against the slow version on many random strings.

## 11. KMP: searching with the prefix function

### From the prefix function to a search

KMP (Knuth, Morris, Pratt) uses the prefix function of the **pattern** to search a text without ever moving backwards in the text. The state is a single number `k`: *how many letters of the pattern are matched right now*.

For each text letter `ch`:

1. While `k > 0` and `ch` does not match `pattern[k]`, fall back: `k = pi[k - 1]`.
2. If `ch` matches `pattern[k]`, then `k += 1`.
3. If `k == m` (the whole pattern matched), we found an occurrence ending at this position. Record it, then fall back `k = pi[k - 1]` so overlapping occurrences are found too.

```python
def kmp_search(text, pattern):
    """Start indices of all (possibly overlapping) occurrences. pattern must not be empty."""
    m = len(pattern)
    pi = prefix_function(pattern)
    found = []
    k = 0
    for i, ch in enumerate(text):
        while k > 0 and ch != pattern[k]:
            k = pi[k - 1]
        if ch == pattern[k]:
            k += 1
        if k == m:
            found.append(i - m + 1)
            k = pi[k - 1]
    return found

print(kmp_search("abcabcabd", "abcabd"))
print(kmp_search("aaaaa", "aa"))
print(kmp_search("abababab", "abab"))
print(kmp_search("hello", "xyz"))
print(kmp_search("abc", "abc"))
```
```text
[3]
[0, 1, 2, 3]
[0, 2, 4]
[]
[0]
```

The second answer, `[0, 1, 2, 3]`, shows that overlapping matches are counted. The reset `k = pi[k - 1]` after a match is what makes that work: after matching `aa`, the border `a` is still matched.

### Hand trace on the text from the picture

Let us watch `k` while searching `abcabd` in `abcabcabd`.

```python
def trace_kmp(text, pattern):
    pi = prefix_function(pattern)
    m = len(pattern)
    k = 0
    print(f"pi of the pattern: {pi}")
    for i, ch in enumerate(text):
        k_before = k
        notes = []
        while k > 0 and ch != pattern[k]:
            notes.append(f"{ch}!={pattern[k]}, k->{pi[k - 1]}")
            k = pi[k - 1]
        if ch == pattern[k]:
            k += 1
        print(f"i={i} text[i]={ch} k {k_before} -> {k}  {'; '.join(notes)}")
        if k == m:
            print(f"   match ends at i={i}, starts at {i - m + 1}")
            k = pi[k - 1]

trace_kmp("abcabcabd", "abcabd")
```
```text
pi of the pattern: [0, 0, 0, 1, 2, 0]
i=0 text[i]=a k 0 -> 1  
i=1 text[i]=b k 1 -> 2  
i=2 text[i]=c k 2 -> 3  
i=3 text[i]=a k 3 -> 4  
i=4 text[i]=b k 4 -> 5  
i=5 text[i]=c k 5 -> 3  c!=d, k->2
i=6 text[i]=a k 3 -> 4  
i=7 text[i]=b k 4 -> 5  
i=8 text[i]=d k 5 -> 6  
   match ends at i=8, starts at 3
```

Look at `i = 5` (the second `c`). We had matched `abcab` (`k = 5`). The pattern wants `d`, the text gives `c`. KMP falls back to `pi[4] = 2` (we still hold `ab`), then compares `c` against `pattern[2] = c`: match, `k = 3`. The text pointer never moved back. The remaining letters `abd` complete the match.

### Complexity

- Building `pi`: `O(m)`.
- The search loop: the same amortised argument as before, `k` rises at most once per text letter, so total fallbacks are at most `n`. So `O(n)`.
- Total **`O(n + m)` time**, **`O(m)` extra space** (the `pi` array).

Compare with the naive count from section 1.

```python
def kmp_count_compares(text, pattern):
    m = len(pattern)
    pi = prefix_function(pattern)
    k = 0
    compares = 0
    for ch in text:
        while k > 0:
            compares += 1
            if ch == pattern[k]:
                break
            k = pi[k - 1]
        else:
            compares += 1
        if ch == pattern[k]:
            k += 1
        if k == m:
            k = pi[k - 1]
    return compares

print(kmp_count_compares("a" * 200, "a" * 50 + "b"), "versus naive", naive_count_compares("a" * 200, "a" * 50 + "b")[1])
```
```text
350 versus naive 7650
```

### The "pattern # text" trick

Many solutions avoid the special handling of `k == m` with a neat trick: build `combined = pattern + "#" + text`, where `#` is a character that occurs in neither. Compute the prefix function of `combined`. Every position where `pi == m` is the end of an occurrence. No border can be longer than `m`, because the `#` blocks it.

```python
def kmp_search_combined(text, pattern):
    m = len(pattern)
    pi = prefix_function(pattern + "#" + text)
    return [i - 2 * m for i in range(m + 1, len(pi)) if pi[i] == m]

print(kmp_search_combined("abababab", "abab"))
print(kmp_search_combined("aaaaa", "aa"))
```
```text
[0, 2, 4]
[0, 1, 2, 3]
```

The index in `combined` of the last letter of a match is `i`. The text begins at `m + 1`, so the match ends at text position `i - m - 1` and starts at `i - m - 1 - (m - 1) = i - 2m`. If the separator might appear in the strings, pick another one, or use the direct version.

### Counting occurrences

Counting is just the length of the answer list. Two counts are common.

```python
def count_overlapping(text, pattern):
    return len(kmp_search(text, pattern))

def count_non_overlapping(text, pattern):
    count, next_free = 0, 0
    for start in kmp_search(text, pattern):
        if start >= next_free:               # the match does not touch the last one we counted
            count += 1
            next_free = start + len(pattern)
    return count

text, pattern = "aaaaaaa", "aaa"
print(count_overlapping(text, pattern), count_non_overlapping(text, pattern), text.count(pattern))
```
```text
5 2 2
```

Python's `str.count` counts **non-overlapping** occurrences, so it agrees with the second number. If the problem says "overlapping", `str.count` is the wrong tool. This is a very common surprise.

### Borders, periods and repeated blocks

The prefix function of the **whole** string answers several questions at once.

**All borders.** The last value `pi[n-1]` is the longest border. The next one is `pi[pi[n-1] - 1]`, and so on down to 0.

```python
def all_borders(s):
    pi = prefix_function(s)
    borders = []
    k = pi[-1] if pi else 0
    while k > 0:
        borders.append(s[:k])
        k = pi[k - 1]
    return borders

print(all_borders("abcabcabc"))
print(all_borders("aabaaab"))
print(all_borders("abcd"))
```
```text
['abcabc', 'abc']
['aab']
[]
```

**The smallest period.** A string `s` has period `p` if `s[i] == s[i + p]` for all valid `i`. The smallest period is `n - pi[n-1]`: the longest border leaves the shortest "leftover" block.

**Is `s` a block repeated?** `s` is built from a smaller block repeated two or more times exactly when `p = n - pi[n-1]` divides `n` and `p < n`.

```python
def smallest_period(s):
    return len(s) - prefix_function(s)[-1]

def repeated_block(s):
    """Return the smallest block that repeats to make s, or None."""
    n = len(s)
    p = smallest_period(s)
    if p < n and n % p == 0:
        return s[:p]
    return None

for s in ["abcabcabc", "ababab", "abaab", "aaaa", "abcab", "z"]:
    print(f"{s!r:12} period={smallest_period(s)}  block={repeated_block(s)!r}")
```
```text
'abcabcabc'  period=3  block='abc'
'ababab'     period=2  block='ab'
'abaab'      period=3  block=None
'aaaa'       period=1  block='a'
'abcab'      period=3  block=None
'z'          period=1  block=None
```

Check `abcab`: its longest border is `ab` (2), so the period is `5 - 2 = 3`. It looks like `abc` repeated, but only one and two-thirds times, so it is not an exact repetition, and `3` does not divide `5`. That is exactly why the second test (`n % p == 0`) is needed: `abcab` has period 3 but is not a repeated block.

Another famous one-liner does the same thing with the built-in `in`: `s in (s + s)[1:-1]`. It is true exactly when `s` is a repeated block. Test both.

```python
import random

def repeated_via_in(s):
    return s in (s + s)[1:-1]

random.seed(7)
ok = True
for _ in range(2000):
    s = "".join(random.choice("ab") for _ in range(random.randint(1, 10)))
    if (repeated_block(s) is not None) != repeated_via_in(s):
        ok = False
print("both methods agree on 2000 random strings:", ok)
```
```text
both methods agree on 2000 random strings: True
```

### Shortest palindrome by adding letters in front

*You may add letters only at the front of `s`. What is the shortest palindrome you can get?* The answer is: find the longest **palindromic prefix** of `s`, and put the reverse of the rest in front.

A prefix of `s` that is a palindrome is a string equal to its own reverse. So it is a border of `s + "#" + reversed(s)`. The prefix function at the last position of that combined string is the length of the longest palindromic prefix.

```python
def shortest_palindrome(s):
    if not s:
        return s
    pi = prefix_function(s + "#" + s[::-1])
    longest_pal_prefix = pi[-1]
    return s[longest_pal_prefix:][::-1] + s

print(shortest_palindrome("aacecaaa"))
print(shortest_palindrome("abcd"))
print(shortest_palindrome("race"))
print(shortest_palindrome("aba"))
```
```text
aaacecaaa
dcbabcd
ecarace
aba
```

### How often does each prefix occur?

Another use: *for every length `k`, how many times does the prefix `s[:k]` occur anywhere in `s`?* Every position `i` ends a prefix of length `pi[i]`, and, by following borders, also all shorter borders. Counting this naively walks chains; counting smartly pushes the numbers down.

```python
def prefix_occurrences(s):
    n = len(s)
    pi = prefix_function(s)
    cnt = [0] * (n + 1)
    for i in range(n):
        cnt[pi[i]] += 1                  # the longest border at i
    for k in range(n - 1, 0, -1):
        cnt[pi[k - 1]] += cnt[k]         # a prefix of length k also contains its own border
    return [c + 1 for c in cnt[1:]]      # +1: the prefix itself, at position 0

print(prefix_occurrences("ababa"))
print(prefix_occurrences("aaaa"))
```
```text
[3, 2, 2, 1, 1]
[4, 3, 2, 1]
```

For `ababa` the printed list says: the prefix `a` occurs 3 times (positions 0, 2, 4), `ab` 2 times (0 and 2), `aba` 2 times (0 and 2, overlapping), `abab` once and `ababa` once. For `aaaa` the prefix of length `k` occurs `4 - k + 1` times. Note that the count includes overlapping occurrences.

### Where the prefix function and KMP fit

| Question | Prefix-function answer |
|---|---|
| Every occurrence of `p` in `t` | KMP search, or `pi` of `p + "#" + t` |
| Longest border of `s` | `pi[-1]` |
| Smallest period | `n - pi[-1]` |
| Is `s` a repeated block? | `p = n - pi[-1]`, `p < n` and `n % p == 0` |
| Longest palindromic prefix | `pi[-1]` of `s + "#" + reversed(s)` |

## 12. The Z-function

### A different table for a similar job

The prefix function looks **backwards**: how long is the border ending here? The **Z-function** looks **forwards**: how much of the string's own beginning matches starting here?

> `z[i]` = the length of the longest string that is a prefix of `s` and also begins at position `i` of `s`.

Equivalently, the length of the common prefix of `s` and `s[i:]`. By convention `z[0]` is set to `n` (the whole string matches itself), though some books leave it 0. We will use `n`.

```python
def z_slow(s):
    n = len(s)
    z = [0] * n
    if n:
        z[0] = n
    for i in range(1, n):
        k = 0
        while i + k < n and s[k] == s[i + k]:
            k += 1
        z[i] = k
    return z

print(z_slow("aabxaab"))
print(z_slow("aaaa"))
print(z_slow("abcd"))
```
```text
[7, 1, 0, 0, 3, 1, 0]
[4, 3, 2, 1]
[4, 0, 0, 0]
```

For `aabxaab`: at position 1 the suffix `abxaab` shares just `a` with `aabxaab` (the second letters differ: `b` versus `a`), so `z[1] = 1`. At position 4 the suffix `aab` equals the first three letters, so `z[4] = 3`. The slow version costs `O(n^2)` in the worst case (all `a`s).

### The linear algorithm: the Z-box

Idea: remember the rightmost segment `[l, r)` found so far that **matches a prefix** (called the **Z-box**): `s[l:r] == s[0:r-l]`. When we reach a new position `i` inside this box, we already know something about it, because the box is a copy of the beginning of the string:

> `s[i]` corresponds to `s[i - l]`, so `z[i]` is at least `min(z[i - l], r - i)`.

Then we only extend by comparing new letters beyond `r`. The box never moves left, and `r` only grows, so the total work is `O(n)`.

```python
def z_function(s):
    n = len(s)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n
    l, r = 0, 0                              # the Z-box is s[l:r]
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])      # reuse the copy
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1                        # extend by new comparisons
        if i + z[i] > r:
            l, r = i, i + z[i]               # a new rightmost box
    return z

for text in ["aabxaab", "aaaa", "abcd", "abacaba", ""]:
    print(f"{text!r:10} {z_function(text)}  matches slow: {z_function(text) == z_slow(text)}")
```
```text
'aabxaab'  [7, 1, 0, 0, 3, 1, 0]  matches slow: True
'aaaa'     [4, 3, 2, 1]  matches slow: True
'abcd'     [4, 0, 0, 0]  matches slow: True
'abacaba'  [7, 0, 1, 0, 3, 0, 1]  matches slow: True
''         []  matches slow: True
```

### Hand trace

Let us trace `aabxaab` and print the box before and after each position.

```python
def trace_z(s):
    n = len(s)
    z = [0] * n
    z[0] = n
    l, r = 0, 0
    print(f"{'i':>2} {'box before':>10} {'start':>5} {'z[i]':>4} {'box after':>10}")
    for i in range(1, n):
        box_before = (l, r)
        if i < r:
            z[i] = min(r - i, z[i - l])
        start = z[i]
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
        print(f"{i:>2} {str(box_before):>10} {start:>5} {z[i]:>4} {str((l, r)):>10}")
    return z

print(trace_z("aabxaab"))
```
```text
 i box before start z[i]  box after
 1     (0, 0)     0    1     (1, 2)
 2     (1, 2)     0    0     (1, 2)
 3     (1, 2)     0    0     (3, 3)
 4     (3, 3)     0    3     (4, 7)
 5     (4, 7)     1    1     (4, 7)
 6     (4, 7)     0    0     (4, 7)
[7, 1, 0, 0, 3, 1, 0]
```

How to read a row: the column `start` is the value we get for free from the box; `z[i]` is the final value after extending. Rows with `start = 0` are positions outside any box, so everything is compared fresh. A row with `start > 0` is where the Z-box saved us comparisons. Try the same trace on `aaaaaa`: after the first position, almost every row has `start` equal to its final `z[i]`, so no further letters have to be matched.

### Why it is O(n)

Every comparison in the `while` loop either fails (once per `i`, at most `n` total) or succeeds and moves `i + z[i]` one step to the right of the old `r` (it increases `r`). Since `r <= n`, the successful comparisons total at most `n`. So the Z-function is `O(n)` time, `O(n)` space.

The two ingredients are the same as in KMP: **never re-compare a letter you have already matched**.

### Pattern search with Z

Use the same trick as for the prefix function: build `pattern + "#" + text`, compute Z, and report positions where `z[i] == m`.

```python
def z_search(text, pattern):
    m = len(pattern)
    z = z_function(pattern + "#" + text)
    return [i - m - 1 for i in range(m + 1, len(z)) if z[i] >= m]

print(z_search("abababab", "abab"))
print(z_search("aaaaa", "aa"))
print(z_search("abcabcabd", "abcabd"))
print(z_search("hello", "xyz"))
```
```text
[0, 2, 4]
[0, 1, 2, 3]
[3]
[]
```

Why `z[i] >= m` and not `== m`? The separator makes it impossible to exceed `m`, so both work here; `>=` is the safer habit when you are not sure of the separator.

### Uses of the Z-function

**1. Pattern matching** (above).

**2. The smallest period.** `p` is a period of `s` exactly if `z[p] == n - p` (the suffix from `p` matches the prefix all the way to the end). The smallest such `p` is the answer.

```python
def period_via_z(s):
    n = len(s)
    z = z_function(s)
    for p in range(1, n):
        if z[p] == n - p:
            return p
    return n

for s in ["abcabcabc", "abcab", "aaaa", "abcd"]:
    print(s, period_via_z(s), smallest_period(s))
```
```text
abcabcabc 3 3
abcab 3 3
aaaa 1 1
abcd 4 4
```

**3. Longest common prefix of the string with each suffix** (the definition itself). For example, the total of all `z[i]` is the number of (position, length) pairs where the prefix of that length repeats.

**4. Counting distinct substrings, and similar problems.** These use the Z-function of reversed prefixes and are a classic exercise. We leave them as practice.

### Z or prefix function?

They are two views of the same information; either can be converted into the other in `O(n)`. Which to learn first? A rough guide:

| | Prefix function | Z-function |
|---|---|---|
| Idea | border ending at `i` | prefix match starting at `i` |
| Natural for | streaming matching (KMP), borders, periods | "how similar is each suffix to the whole string" |
| Can process | text one letter at a time, never storing it | needs the whole string first |
| Code | `while` fallback | maintain a box `[l, r)` |
| Cost | `O(n)` | `O(n)` |

If you need to match a pattern against a **stream** of letters (you cannot look back), KMP is the tool. If the problem says "for every suffix, compare with the whole string", Z is the tool.

## 13. Rabin-Karp: searching with fingerprints

### The idea

KMP and Z avoid wasted comparisons by remembering matched letters. Rabin-Karp takes a different road: give every string of length `m` a **fingerprint** (a hash), and compare numbers instead of strings. A window of the text can only equal the pattern if their fingerprints are equal.

This works only if we can get the fingerprint of the **next** window without reading all `m` letters again. That is the **rolling hash**, and it is why the polynomial hash of dsa.04, section 12 was built the way it was.

### The rolling update

With letter values `v` and base `B`, the hash of a window `w0 w1 ... w(m-1)` is

```text
H = v(w0) * B^(m-1) + v(w1) * B^(m-2) + ... + v(w(m-1))      (mod M)
```

Slide the window one step right: drop `w0` at the front, add a new letter `x` at the back.

```text
H_new = (H - v(w0) * B^(m-1)) * B + v(x)       (mod M)
```

Subtracting removes the first letter's term; multiplying by `B` shifts every remaining letter one place up; adding `v(x)` appends the new letter. Each slide is `O(1)`.

```python
def rolling_hashes(text, m, B=31, M=101):
    """Hash of every window of length m, using the rolling update."""
    value = lambda ch: ord(ch) - 96
    top = pow(B, m - 1, M)               # B^(m-1) mod M, computed once
    h = 0
    for ch in text[:m]:
        h = (h * B + value(ch)) % M
    out = [h]
    for i in range(m, len(text)):
        h = ((h - value(text[i - m]) * top) * B + value(text[i])) % M
        out.append(h)
    return out

def direct_hash(s, B=31, M=101):
    h = 0
    for ch in s:
        h = (h * B + (ord(ch) - 96)) % M
    return h

text = "abcabcab"
rolled = rolling_hashes(text, 3)
direct = [direct_hash(text[i:i + 3]) for i in range(len(text) - 2)]
print(rolled)
print(direct)
print(rolled == direct)
```
```text
[16, 97, 88, 16, 97, 88]
[16, 97, 88, 16, 97, 88]
True
```

The rolling hashes equal the hashes computed from scratch, and equal windows (`abc` at 0 and 3) have equal numbers (the first and fourth entries match). Python's built-in `pow(B, m - 1, M)` computes `B^(m-1) mod M` quickly without making a huge number.

### The search

```python
def rabin_karp(text, pattern, B=131, M=1_000_000_007, verify=True):
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    top = pow(B, m - 1, M)
    hp = ht = 0
    for i in range(m):
        hp = (hp * B + ord(pattern[i])) % M
        ht = (ht * B + ord(text[i])) % M
    found = []
    for start in range(n - m + 1):
        if ht == hp:
            if not verify or text[start:start + m] == pattern:
                found.append(start)
        if start + m < n:
            ht = ((ht - ord(text[start]) * top) * B + ord(text[start + m])) % M
    return found

print(rabin_karp("abcabcabd", "abcabd"))
print(rabin_karp("aaaaa", "aa"))
print(rabin_karp("hello", "xyz"))
print(rabin_karp("abababab", "abab"))
```
```text
[3]
[0, 1, 2, 3]
[]
[0, 2, 4]
```

Here the letter value is the character code `ord(ch)`; any value from 1 up works. The `verify` flag matters; see below.

### Trap 1: the modulus and negative numbers

The subtraction `ht - ord(text[start]) * top` can be negative before the `% M`. In **Python** the `%` operator always returns a number between 0 and `M - 1`, so the code above is safe. In C, C++ and Java the remainder of a negative number is negative, and a negative hash then never equals a good hash. The fix there is `((x % M) + M) % M`.

We can mimic the C behaviour to see the damage.

```python
def c_remainder(a, m):
    """The % of C and Java: the sign follows the left side."""
    r = abs(a) % m
    return r if a >= 0 else -r

M = 101
print("Python:", (5 - 9 * 3) % M, "| C-style:", c_remainder(5 - 9 * 3, M))

def rolling_c_style(text, m, B=31):
    value = lambda ch: ord(ch) - 96
    top = pow(B, m - 1, M)
    h = 0
    for ch in text[:m]:
        h = c_remainder(h * B + value(ch), M)
    out = [h]
    for i in range(m, len(text)):
        h = c_remainder((h - value(text[i - m]) * top) * B + value(text[i]), M)
        out.append(h)
    return out

print(rolling_c_style("abcabcab", 3))
print(rolling_hashes("abcabcab", 3))
```
```text
Python: 79 | C-style: -22
[16, -4, -13, -85, -4, -13]
[16, 97, 88, 16, 97, 88]
```

The C-style list contains negative numbers, and some of its entries differ from the correct ones, although they are equal modulo 101. A negative and a positive number with the same remainder never compare equal with `==`. The matching windows would be missed.

### Trap 2: collisions

Different strings can have the same hash. With a small modulus it happens all the time. Let us count **false alarms**: windows whose hash equals the pattern's hash, although the strings differ.

```python
import random

def false_alarms(text, pattern, B, M):
    m = len(pattern)
    hits = 0
    for start in range(len(text) - m + 1):
        window = text[start:start + m]
        if direct_hash_general(window, B, M) == direct_hash_general(pattern, B, M) and window != pattern:
            hits += 1
    return hits

def direct_hash_general(s, B, M):
    h = 0
    for ch in s:
        h = (h * B + ord(ch)) % M
    return h

random.seed(3)
text = "".join(random.choice("abcd") for _ in range(2000))
pattern = "abcdabcd"
print("windows:", len(text) - len(pattern) + 1)
for M in [11, 101, 10007, 1_000_000_007]:
    print(f"M={M:>10}  false alarms: {false_alarms(text, pattern, 131, M)}")
```
```text
windows: 1993
M=        11  false alarms: 151
M=       101  false alarms: 27
M=     10007  false alarms: 0
M=1000000007  false alarms: 0
```

With `M = 11` roughly one window in ten is a false alarm. With a modulus near a billion there are almost none: the chance for one pair is about `1 / M`. But almost none is not none. So there are two kinds of Rabin-Karp.

| Version | When hashes match | Guarantee |
|---|---|---|
| **Verifying** (Las Vegas) | compare the strings letter by letter | always correct; expected `O(n + m)`, worst `O(n * m)` |
| **Trusting** (Monte Carlo) | accept the match | very fast, but wrong with a tiny probability |

For a contest, trusting is common. For anything where a wrong answer is costly, verify. The cost of verifying is small: it only happens on a hash match, and real matches must be compared anyway.

### Defence 1: double hashing

Use **two** independent hashes (different base *and* different modulus) and call two windows equal only if **both** agree. The collision chances multiply: about `1 / (M1 * M2)`.

```python
def double_hash(s, params=((131, 1_000_000_007), (137, 998_244_353))):
    out = []
    for B, M in params:
        h = 0
        for ch in s:
            h = (h * B + ord(ch)) % M
        out.append(h)
    return tuple(out)

def false_alarms_double(text, pattern, params):
    m = len(pattern)
    target = double_hash(pattern, params)
    return sum(1 for s in range(len(text) - m + 1)
               if text[s:s + m] != pattern and double_hash(text[s:s + m], params) == target)

weak = ((131, 101), (137, 103))
print("single hash, M=101      :", false_alarms(text, pattern, 131, 101))
print("double hash, M=101, 103 :", false_alarms_double(text, pattern, weak))
print("double hash, big moduli :", false_alarms_double(text, pattern, ((131, 1_000_000_007), (137, 998_244_353))))
```
```text
single hash, M=101      : 27
double hash, M=101, 103 : 0
double hash, big moduli : 0
```

Even with the tiny moduli 101 and 103, using both hashes cuts the false alarms to almost nothing. Tuples compare with `==` and can be stored in sets or used as dict keys, which makes double hashing easy in Python.

### Defence 2: a random base

If the base and the modulus are fixed and known (for instance, in a contest where others can read your code), somebody can build two strings with the same hash on purpose. A random base chosen when the program starts defeats this.

```python
M = 1_000_000_007
B = random.randrange(300, M - 1)
print(300 <= B < M)
```
```text
True
```

Pick a base larger than the alphabet size (so every letter value is smaller than `B`) and smaller than `M`.

### Complexity

| | Time | Space |
|---|---|---|
| Hash the pattern and the first window | `O(m)` | `O(1)` |
| Slide over the text | `O(n)` | `O(1)` |
| Verifying matches | `O(m)` per hash match | `O(1)` |
| **Total, expected** | **`O(n + m)`** | `O(1)` |
| **Worst case with verification** | `O(n * m)` (for example the text is all `a` and the pattern is all `a`, so every window is a real match and each is verified) | `O(1)` |

The worst case is not a flaw of the hash: if the pattern really occurs at `n` places, there are `n` answers, and writing the answers alone (or verifying them) costs `n * m`. To list only the *start positions* in `O(n + m)` for that case, skip verification (accept the tiny risk), or use KMP, whose cost is exactly `O(n + m)` always.

### Searching for many patterns of the same length

Rabin-Karp shines when there are **many patterns of equal length**: keep the hashes of all patterns in a set, and check each window against the set once.

```python
def find_any(text, patterns):
    m = len(patterns[0])
    assert all(len(p) == m for p in patterns)
    B, M = 131, 1_000_000_007
    top = pow(B, m - 1, M)
    wanted = {}
    for p in patterns:
        h = 0
        for ch in p:
            h = (h * B + ord(ch)) % M
        wanted.setdefault(h, []).append(p)
    h = 0
    for ch in text[:m]:
        h = (h * B + ord(ch)) % M
    hits = []
    for start in range(len(text) - m + 1):
        for p in wanted.get(h, []):
            if text[start:start + m] == p:
                hits.append((start, p))
        if start + m < len(text):
            h = ((h - ord(text[start]) * top) * B + ord(text[start + m])) % M
    return hits

print(find_any("the cat sat on the mat", ["cat", "sat", "mat", "dog"]))
```
```text
[(4, 'cat'), (8, 'sat'), (19, 'mat')]
```

One pass, any number of equal-length patterns, expected `O(n + k * m)` for `k` patterns. KMP would need `k` passes. (Patterns of different lengths need one pass per distinct length, or the Aho-Corasick automaton, which is a trie with KMP-style fallback links and is beyond this module.)

## 14. Hash a substring in O(1): finding repeated substrings

### Prefix hashes

Rolling windows are perfect for fixed-length windows. For arbitrary substrings `s[l:r]` we use **prefix hashes** (dsa.04, section 12): `H[i]` is the hash of `s[:i]`, and `P[i]` is `B^i`. Then

```text
hash(s[l:r]) = (H[r] - H[l] * P[r - l]) mod M
```

After `O(n)` preparation, any substring hash costs `O(1)`.

```python
class StringHash:
    def __init__(self, s, B=131, M=(1 << 61) - 1):
        self.M = M
        self.H = [0] * (len(s) + 1)
        self.P = [1] * (len(s) + 1)
        for i, ch in enumerate(s):
            self.H[i + 1] = (self.H[i] * B + ord(ch)) % M
            self.P[i + 1] = (self.P[i] * B) % M

    def get(self, l, r):
        """Hash of s[l:r]."""
        return (self.H[r] - self.H[l] * self.P[r - l]) % self.M

s = "abracadabra"
sh = StringHash(s)
print(sh.get(0, 4) == sh.get(7, 11), s[0:4], s[7:11])     # abra and abra
print(sh.get(0, 4) == sh.get(1, 5), s[0:4], s[1:5])       # abra and brac
```
```text
True abra abra
False abra brac
```

The modulus `2^61 - 1` is a prime commonly used for hashing: with it, two different strings collide with probability around `10^-18`, small enough to trust in practice. Python integers do not overflow, so the multiplication of two 61-bit numbers is fine.

### The problem: longest repeated substring

*Find the longest substring that occurs at least twice in `s` (the two occurrences may overlap).* For `"banana"` the answer is `"ana"` (positions 1 and 3, overlapping).

Brute force compares all pairs of substrings: far too slow. Two observations make it fast.

1. **Monotone:** if some substring of length `L` occurs twice, then some substring of length `L - 1` occurs twice as well (just drop its last letter from both copies). So "a repeat of length `L` exists" is true for small `L` and false for large `L`.
2. **Checking one length is cheap:** hash all `n - L + 1` windows of length `L`, and see if any hash appears twice.

That is exactly the "binary search on the answer" pattern of dsa.06.

```python
def has_repeat(s, L, sh):
    """Return a start index of a repeated window of length L, or -1."""
    seen = {}
    for i in range(len(s) - L + 1):
        h = sh.get(i, i + L)
        if h in seen:
            j = seen[h]
            if s[j:j + L] == s[i:i + L]:         # verify: guards against a collision
                return i
        else:
            seen[h] = i
    return -1

def longest_repeated_substring(s):
    sh = StringHash(s)
    lo, hi = 0, len(s) - 1                        # the answer length is in [lo, hi]
    best = ""
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid == 0:
            lo = 1
            continue
        i = has_repeat(s, mid, sh)
        if i != -1:
            best = s[i:i + mid]
            lo = mid + 1                          # try longer
        else:
            hi = mid - 1                          # too long
    return best

for word in ["banana", "abcd", "aaaaa", "abracadabra", "mississippi", ""]:
    print(f"{word!r:14} -> {longest_repeated_substring(word)!r}")
```
```text
'banana'       -> 'ana'
'abcd'         -> ''
'aaaaa'        -> 'aaaa'
'abracadabra'  -> 'abra'
'mississippi'  -> 'issi'
''             -> ''
```

Let us check it against a slow, obviously correct version on many random strings. If they ever differ in **length**, the fast one is wrong (the strings themselves may differ when there are ties).

```python
def lrs_slow(s):
    best = ""
    n = len(s)
    for L in range(1, n):
        seen = set()
        for i in range(n - L + 1):
            w = s[i:i + L]
            if w in seen:
                best = w
                break
            seen.add(w)
    return best

random.seed(11)
bad = 0
for _ in range(500):
    s = "".join(random.choice("abc") for _ in range(random.randint(0, 14)))
    if len(longest_repeated_substring(s)) != len(lrs_slow(s)):
        bad += 1
print("disagreements out of 500:", bad)
```
```text
disagreements out of 500: 0
```

### Complexity

- Preparation: `O(n)`.
- One check for a length: `O(n)` hashes (each `O(1)`) plus `O(L)` for each verification of a hash match; a few verifications on average.
- Binary search: `O(log n)` rounds.
- **Total `O(n log n)` expected time, `O(n)` space.** The naive way (put every substring of every length in a set) is `O(n^2)` windows times `O(n)` slice cost.

A suffix array or suffix automaton gives a deterministic `O(n log n)` or `O(n)` answer, but those are heavier machines. Hashing plus binary search is the practical one-page solution.

### The same trick for "Do two substrings match?"

Once a `StringHash` exists, many queries become one-liners.

- *Are `s[a:a+k]` and `s[b:b+k]` equal?* Compare `get(a, a+k)` and `get(b, b+k)`.
- *Longest common prefix of two suffixes?* Binary search on the length, each check `O(1)`: `O(log n)` per query.
- *Is `s[l:r]` a palindrome?* Keep a hash of the reversed string too, and compare. (Manacher answers this and more, exactly, in the next section.)
- *Repeated DNA sequences:* for fixed length 10, a set of the `n - 9` windows works with no hashing at all, because the slices are short. Use hashing when the length is large or variable.

## 15. Manacher's algorithm: all palindromes in linear time

### The problem

A **palindrome** reads the same forwards and backwards (`racecar`, `abba`, `a`). Typical questions:

- Find the **longest palindromic substring**.
- **Count** how many substrings are palindromes.
- Answer "is `s[l:r]` a palindrome?" quickly for many queries.

### The easy way: expand around a centre

Every palindrome has a **centre**: a letter (odd length) or the gap between two letters (even length). A string of length `n` has `2n - 1` centres. From each centre, grow outwards while the letters on both sides match.

```python
def expand(s, left, right):
    """Grow while s[left] == s[right]. Return the final (left, right), exclusive of the bad ones."""
    while left >= 0 and right < len(s) and s[left] == s[right]:
        left -= 1
        right += 1
    return left + 1, right - 1

def longest_pal_expand(s):
    best = (0, -1)
    for c in range(len(s)):
        for l, r in (expand(s, c, c), expand(s, c, c + 1)):   # odd centre, even centre
            if r - l > best[1] - best[0]:
                best = (l, r)
    return s[best[0]:best[1] + 1]

def count_pal_expand(s):
    total = 0
    for c in range(len(s)):
        for left, right in ((c, c), (c, c + 1)):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                total += 1
                left -= 1
                right += 1
    return total

print(longest_pal_expand("babad"), longest_pal_expand("cbbd"), longest_pal_expand("forgeeksskeegfor"))
print(count_pal_expand("abc"), count_pal_expand("aaa"), count_pal_expand("abba"))
```
```text
bab bb geeksskeeg
3 6 6
```

(`babad` has two correct answers, `bab` and `aba`; this code returns the first one it finds.) The count for `aaa` is 6: `a` three times, `aa` twice and `aaa` once.

The cost: `2n - 1` centres, each growing up to `n / 2`. So `O(n^2)` in the worst case (a string of all `a`). This is fine up to a few thousand letters and too slow for a million.

### The waste, and Manacher's idea

When we expand from a centre, we re-check letters that an earlier centre has already compared. Think of a big palindrome with centre `c`. Inside it, to the right of `c`, everything is the **mirror image** of what is on the left. So the palindromes around positions on the right side are the mirror images of the palindromes around the mirrored positions on the left, at least as far as the big palindrome reaches.

Manacher's algorithm uses that: keep the palindrome that reaches **furthest right**, and start each new centre with the answer of its mirror, only expanding past the edge.

### Making odd and even look the same

To avoid handling two kinds of centre, insert a separator between all letters and at both ends: `"abba"` becomes `"#a#b#b#a#"`. Every palindrome of the original string now has a **letter or `#` as its centre**, and its length in the new string is always odd. The separator must not appear in the string.

Let `p[i]` be the **radius** at `i`: the number of steps we can go in both directions from `i` in the new string `t` while `t[i-k] == t[i+k]`. The magic fact: `p[i]` is exactly the **length of the longest palindrome of the original string centred at `i`**.

```python
def manacher(s):
    t = "#" + "#".join(s) + "#"
    n = len(t)
    p = [0] * n
    c = r = 0                                  # centre and right edge of the rightmost palindrome
    for i in range(n):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])    # copy from the mirror position 2c - i
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1                          # expand beyond what the mirror told us
        if i + p[i] > r:
            c, r = i, i + p[i]
    return t, p

t, p = manacher("babad")
print(t)
print(p)
```
```text
#b#a#b#a#d#
[0, 1, 0, 3, 0, 3, 0, 1, 0, 1, 0]
```

### Hand trace on `babad`

The new string is `#b#a#b#a#d#` (11 characters). Let us print the details of every step: the mirror, the starting radius, and what the expansion added.

```python
def trace_manacher(s):
    t = "#" + "#".join(s) + "#"
    n = len(t)
    p = [0] * n
    c = r = 0
    print(f"{'i':>2} {'t[i]':>4} {'mirror':>6} {'start':>5} {'p[i]':>4} {'(c, r)':>8}")
    for i in range(n):
        mirror = 2 * c - i
        if i < r:
            p[i] = min(r - i, p[mirror])
            shown = mirror
        else:
            shown = "-"
        start = p[i]
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1
        if i + p[i] > r:
            c, r = i, i + p[i]
        print(f"{i:>2} {t[i]:>4} {shown!s:>6} {start:>5} {p[i]:>4} {str((c, r)):>8}")
    return p

trace_manacher("babad")
```
```text
 i t[i] mirror start p[i]   (c, r)
 0    #      -     0    0   (0, 0)
 1    b      -     0    1   (1, 2)
 2    #      -     0    0   (1, 2)
 3    a      -     0    3   (3, 6)
 4    #      2     0    0   (3, 6)
 5    b      1     1    3   (5, 8)
 6    #      4     0    0   (5, 8)
 7    a      3     1    1   (5, 8)
 8    #      -     0    0   (5, 8)
 9    d      -     0    1  (9, 10)
10    #      -     0    0  (9, 10)
```

Read three rows.

- Row `i = 0` is the first `#`: nothing to the left, `p = 0`.
- Row `i = 3` is the letter `a` at index 1 of `babad`. It reaches radius 3, covering `#b#a#b#` in `t`, which stands for `bab` (length 3 = `p`). The rightmost palindrome becomes centre 3, right edge 6.
- Row `i = 5` is the second `b`. Its position is inside the box, and its mirror is `2*3 - 5 = 1`, where `p[1] = 1`. So the start is 1, but the expansion tries more and finds `aba`, radius 3.

Whenever the start radius is positive, the table saved us comparisons. Try the trace on `"aaaaaa"` to see long chains of copied values.

### Reading the answers from p

Because `p[i]` equals the length of the longest palindrome centred at `i`:

- **Longest palindromic substring:** take the maximum of `p`. If it is at index `i`, the palindrome has length `p[i]` and starts at `(i - p[i]) // 2` in the original string.
- **Number of palindromic substrings:** a centre `i` has palindromes of lengths `p[i]`, `p[i] - 2`, `p[i] - 4`, and so on down to 1 or 2 (each shorter one is the same palindrome with its two outer letters removed). That is `(p[i] + 1) // 2` palindromes. Add this up over all `i`.

```python
def longest_palindrome(s):
    if not s:
        return ""
    t, p = manacher(s)
    i = max(range(len(p)), key=lambda k: p[k])
    start = (i - p[i]) // 2
    return s[start:start + p[i]]

def count_palindromes(s):
    t, p = manacher(s)
    return sum((r + 1) // 2 for r in p)

for w in ["babad", "cbbd", "forgeeksskeegfor", "a", "abc", "aaa", "abba"]:
    print(f"{w!r:20} longest={longest_palindrome(w)!r:12} count={count_palindromes(w)}")
```
```text
'babad'              longest='bab'        count=7
'cbbd'               longest='bb'         count=5
'forgeeksskeegfor'   longest='geeksskeeg' count=23
'a'                  longest='a'          count=1
'abc'                longest='a'          count=3
'aaa'                longest='aaa'        count=6
'abba'               longest='abba'       count=6
```

The counts agree with the expansion version above: `aaa` has 6, `abba` has 6 (four single letters, `bb` and `abba`), `abc` has 3.

Let us confirm everything against the slow versions on random strings.

```python
random.seed(5)
problems = 0
for _ in range(1000):
    w = "".join(random.choice("ab") for _ in range(random.randint(1, 16)))
    if len(longest_palindrome(w)) != len(longest_pal_expand(w)) or count_palindromes(w) != count_pal_expand(w):
        problems += 1
print("mismatches out of 1000:", problems)
```
```text
mismatches out of 1000: 0
```

### Why is it O(n)?

The right edge `r` only moves right. A letter comparison in the `while` loop that **succeeds** pushes `i + p[i]` beyond the old `r` (the copied start never goes past `r`, so any extra success reaches new ground). There are at most `n` new ground steps in total. Each `i` has at most one failing comparison. So the total number of comparisons is `O(n)`, the same amortised argument as for the Z-function. The transformed string has length `2n + 1`, so time and space are `O(n)`.

### Is "is this substring a palindrome?" answered?

Yes. The substring `s[l:r]` (with `r` exclusive) has its centre at index `l + r` of `t`, and it is a palindrome exactly when `p[l + r] >= r - l`. That is a constant-time check after the linear preprocessing.

```python
def is_pal_query(p, l, r):
    return p[l + r] >= r - l

t, p = manacher("abacdcaba")
print(is_pal_query(p, 0, 3), is_pal_query(p, 0, 9), is_pal_query(p, 1, 4), is_pal_query(p, 3, 6))
print("abacdcaba"[0:3], "abacdcaba"[0:9], "abacdcaba"[1:4], "abacdcaba"[3:6])
```
```text
True True False True
aba abacdcaba bac cdc
```

### Manacher or something else?

| Method | Time | Space | When |
|---|---|---|---|
| Expand around centres | `O(n^2)` | `O(1)` | `n` up to a few thousand; shortest code |
| Dynamic programming table | `O(n^2)` | `O(n^2)` | when you must also count other things |
| Hashing forward and reverse | `O(n log n)` | `O(n)` | palindrome checks with binary search; has a collision risk |
| **Manacher** | **`O(n)`** | `O(n)` | large `n`; many palindrome queries |

## 16. Which tool for which string problem?

### Python's built-ins come first

Before writing KMP, ask whether the language already has it. These are written in C, heavily optimised, and almost always faster in practice than any pure-Python algorithm of this chapter.

| Built-in | What it does | Notes |
|---|---|---|
| `p in s` | does `p` occur in `s` | no positions |
| `s.find(p)` / `s.index(p)` | first position, or `-1` / error | accepts a start index: `s.find(p, start)` |
| `s.rfind(p)` | last position | |
| `s.count(p)` | **non-overlapping** occurrences | surprising for `"aaaa".count("aa")` |
| `s.startswith(p)` / `s.endswith(p)` | prefix and suffix tests | accept tuples of options |
| `s.replace(a, b)` | replace all non-overlapping occurrences | |
| `s.split(sep)` | cut at each separator | |

A loop that lists all (overlapping) positions with `find`:

```python
def all_positions_find(text, pattern):
    out, start = [], 0
    while True:
        i = text.find(pattern, start)
        if i == -1:
            return out
        out.append(i)
        start = i + 1                      # +1, not + len(pattern): allow overlaps

print(all_positions_find("abababab", "abab"))
print("aaaa".count("aa"), len(all_positions_find("aaaa", "aa")))
```
```text
[0, 2, 4]
2 3
```

CPython's search is a tuned combination of simple scanning and (since Python 3.10) a "two-way" algorithm for long patterns, which makes `find` linear in the worst case and very quick in the typical one. So, for **a plain "where is this pattern" question, use `find`**. The algorithms of this chapter earn their place when the built-ins cannot do the job:

- the question is **not** plain searching (period, border, palindromes, similarity of suffixes);
- you need **many queries** over the same data (a trie, prefix hashes, a Manacher array);
- you must work on a **stream** of letters (KMP's state is one integer);
- you must search for **many patterns**, or compare **windows** (Rabin-Karp);
- the problem is in a course or interview, and the point is to show the algorithm.

### Decision guide

| The question | Reach for | Why |
|---|---|---|
| Does this text contain this pattern? | `in` / `find` | built-in, fast |
| All positions of one pattern, overlaps allowed | `find` in a loop, or KMP | both linear in practice |
| Many words, prefix queries, autocomplete | **trie** | cost depends on the word length only |
| Wildcard `.` in the query | trie plus DFS | branching only where needed |
| Words in a grid | trie plus backtracking | prunes whole branches |
| Max XOR of two numbers | binary trie | greedy bit by bit |
| Longest prefix that is also a suffix; smallest period; "is it a repeated block" | **prefix function** | the answer is `pi[n-1]` |
| Match against a stream, one letter at a time | **KMP** | state is one integer |
| How much of the beginning matches at each position | **Z-function** | that is its definition |
| Many equal-length patterns; compare windows or substrings | **Rabin-Karp / prefix hashes** | one number per window |
| Longest repeated substring | hashing plus binary search | monotone property |
| Longest palindromic substring, count of palindromes | **Manacher** (or expand if `n` small) | `O(n)` for all centres |
| Palindromes after adding letters to the front | prefix function on `s + "#" + reversed(s)` | longest palindromic prefix |

### Complexity table

| Algorithm | Time | Extra space | Notes |
|---|---|---|---|
| Trie insert / search / starts_with / delete | `O(L)` | `O(total letters)` | `L` = length of the word |
| Trie autocomplete | `O(p + S)` | `O(L)` stack | `p` = prefix length, `S` = size of the subtree |
| Word Search II | `O(R * C * 3^L)` | `O(total letters)` | independent of the number of words |
| XOR trie | `O(n * B)` | `O(n * B)` | `B` = number of bits |
| Naive search | `O(n * m)` | `O(1)` | the baseline |
| Prefix function | `O(m)` | `O(m)` | amortised |
| KMP search | `O(n + m)` | `O(m)` | always, never backs up in the text |
| Z-function | `O(n)` | `O(n)` | amortised |
| Rabin-Karp | `O(n + m)` expected, `O(n * m)` worst | `O(1)` | collisions; verify or double hash |
| Longest repeated substring (hash + binary search) | `O(n log n)` expected | `O(n)` | |
| Manacher | `O(n)` | `O(n)` | all palindromes |
| Expand around centres | `O(n^2)` | `O(1)` | |

### A compact tour

A single string, `abcabcab`, asked four different questions: where does `abcab` occur, what is its period, what is its longest border, and does the prefix function agree with Z?

```python
s = "abcabcab"
print("positions of 'abcab':", kmp_search(s, "abcab"))
print("pi:", prefix_function(s))
print("z :", z_function(s))
print("smallest period:", smallest_period(s), "| longest border:", all_borders(s)[0])
print("period from z  :", period_via_z(s))
```
```text
positions of 'abcab': [0, 3]
pi: [0, 0, 0, 1, 2, 3, 4, 5]
z : [8, 0, 0, 5, 0, 0, 2, 0]
smallest period: 3 | longest border: abcab
period from z  : 3
```

The two arrays tell the same story from two directions. `pi[7] = 5` says "the last 5 letters equal the first 5". `z[3] = 5` says "from position 3, the next 5 letters equal the first 5". They are the same fact.

## 17. Common traps, collected

1. **Forgetting `is_end`.** Without the end flag, `search("ca")` returns true for a trie that only holds `car`. A prefix is not a word.
2. **Mixing up `search` and `starts_with`.** One checks the flag, the other does not.
3. **Trie memory.** One node per letter of unshared text, each with a dict or a 26-slot list. A million letters can use hundreds of megabytes in Python. For small alphabets use arrays; for few, long words a `set` with `startswith` may be better; for static data a sorted list and `bisect` finds prefix ranges with no nodes at all.
4. **Deleting without pruning, or pruning too far.** After clearing `is_end`, remove nodes bottom-up, and stop at a node that still has children or is another word's end.
5. **Not restoring state in backtracking.** In Word Search II every cell marked `#` must be restored, or later paths see a damaged board.
6. **Reporting a word twice.** In Word Search II, take the word out of the trie when you find it.
7. **Off-by-one in the prefix function.** The fallback is `pi[k - 1]`, not `pi[k]`. The compared letter is `s[k]`.
8. **Not resetting after a full match in KMP.** After `k == m`, set `k = pi[k - 1]` so the next letter does not read past the pattern.
9. **Using `str.count` for overlapping matches.** `"aaaa".count("aa")` is 2, not 3.
10. **A separator that occurs in the text.** The `#` in `pattern + "#" + text` must be a letter that appears in neither string, or the borders can cross it.
11. **The period test without the divisibility check.** `n - pi[n-1]` is a period; it is a *block repetition* only when it divides `n`.
12. **Negative numbers after a subtraction modulo `M`.** In Python `%` fixes it. In C, C++ or Java add `M` before the final `%`.
13. **A hash that treats `a` as 0.** `a`, `aa`, `aaa` then all collide. Start letter values at 1.
14. **Trusting a hash match.** A hash match means "probably equal". Verify, or use two hashes, or a huge modulus such as `2^61 - 1`.
15. **A small modulus.** With `M = 101` false alarms are common. Use at least about `10^9`, and a random base.
16. **Overflow worries in other languages.** Python integers are unbounded, so the product `h * B` is safe, but may become slow if you forget the `% M`.
17. **Manacher without the separators.** Without `#`, odd and even palindromes need separate code. Insert the separator, and remember that `p[i]` is then the *length*, not the radius in the original.
18. **Reading the Manacher start index wrongly.** The palindrome of radius `p[i]` centred at `i` of `t` starts at `(i - p[i]) // 2` in `s`.
19. **Case, spaces and punctuation.** "Palindrome" problems on sentences usually lower-case and drop non-letters first. Do that before the algorithm.
20. **An empty string or a pattern longer than the text.** Test `""`, a one-letter string, a pattern equal to the text, and `m > n`.

## 18. Summary

- A **trie** stores words as paths of letters from a root. Words that share a prefix share nodes. `insert`, `search`, `starts_with` and `delete` cost `O(L)` for a word of length `L`, whatever the number of words. A node needs an **end flag**, because a prefix is not a word.
- Children can be a **dict** (any alphabet, simple) or a **26-slot list** (fixed small alphabet, indexed by `ord(ch) - 97`). Counts on the nodes give "how many words start with this prefix" in `O(p)`.
- Trie uses: **autocomplete** (walk to the prefix, then DFS), **top-k** by frequency, **longest common prefix** (walk while there is exactly one child and no word ends), **replace words** (stop at the first word end), **wildcard search** (branch at `.`), **Word Search II** (one DFS guided by the trie, pruned branches), and the **XOR trie** (binary trie, prefer the opposite bit).
- The **prefix function** `pi[i]` is the longest proper border of `s[:i+1]`. It is computed in `O(n)` by falling back with `k = pi[k - 1]`; the cost is amortised, because `k` rises by at most 1 per step.
- **KMP** runs the prefix function of the pattern over the text: `O(n + m)`, never moving back in the text. After a full match, fall back with `k = pi[k - 1]` to catch overlaps.
- From `pi`: **borders** (follow `pi[pi[n-1] - 1]`), **smallest period** `n - pi[n-1]`, **repeated block** (period divides `n`), **longest palindromic prefix** (`pi` of `s + "#" + reversed(s)`), and prefix occurrence counts.
- The **Z-function** `z[i]` is the length of the match between `s` and `s[i:]`. It is computed in `O(n)` with a **Z-box** `[l, r)` that stores the rightmost match. Pattern search is `z` of `pattern + "#" + text`.
- **Rabin-Karp** slides a **rolling hash** across the text: `h = ((h - out * B^(m-1)) * B + in) % M`. Expected `O(n + m)`. Traps: negative remainders (non-Python), collisions, a weak modulus, letters valued 0. Defences: verify matches, **double hashing**, a random base, a big modulus.
- With **prefix hashes**, any substring hash is `O(1)`. **Longest repeated substring** is binary search on the length plus a set of window hashes, `O(n log n)`.
- **Manacher** inserts `#` between letters and keeps the palindrome that reaches furthest right, copying the answer of the mirror position and expanding only beyond the edge. `p[i]` is the length of the longest palindrome centred at `i`. Longest palindromic substring and the number of palindromes both come out in `O(n)`.
- Use the built-ins (`in`, `find`, `startswith`) for plain searching. Reach for these algorithms for structure questions (period, border, palindromes), many queries, streams and many patterns.

### Learning outcomes checklist

- [ ] I can write a trie with dict nodes and explain why `is_end` is needed.
- [ ] I can write the array-node version and say when it is the better choice.
- [ ] I can delete a word and prune the nodes that are no longer needed.
- [ ] I can build autocomplete, wildcard search and Word Search II on a trie.
- [ ] I can compute the prefix function by hand and in code, and explain why it is `O(n)`.
- [ ] I can use it for KMP search, borders, periods and repeated blocks.
- [ ] I can compute the Z-function, trace the Z-box, and use it to search.
- [ ] I can write Rabin-Karp, name its traps and use double hashing.
- [ ] I can find the longest repeated substring with hashing and binary search.
- [ ] I can run Manacher's algorithm and read the longest palindrome and the count from `p`.
- [ ] I can choose between a built-in, a trie, KMP, Z, a hash and Manacher for a given problem.
