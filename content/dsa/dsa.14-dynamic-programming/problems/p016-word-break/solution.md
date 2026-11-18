## Approach

The recipe from chapter section 5:

- **State:** `f(i)` = `True` if `s[:i]` can be cut into words.
- **Transition:** `f(i)` is `True` if some cut `j < i` has `f(j)` `True` and `s[j:i]` in the word set.
- **Base:** `f(0) = True`.
- **Answer:** `f(n)`.

Two speed-ups: a `set` for the words, and `j` only from `i - longest` (no word is longer).

```python
def word_break(s, words):
    word_set = set(words)
    longest = max((len(w) for w in word_set), default=0)
    n = len(s)
    f = [False] * (n + 1)
    f[0] = True                                    # the empty prefix needs no cut
    for i in range(1, n + 1):
        for j in range(max(0, i - longest), i):
            if f[j] and s[j:i] in word_set:
                f[i] = True
                break
    return f[n]
```

## Complexity

`n` states, at most `L` cut points each (`L` = longest word), and a slice plus a hash of up to `L` characters per cut point: `O(n * L^2)`. Without the `longest` limit it is `O(n^2)` cut points and `O(n^3)` characters in the worst case.

## Another way

Top-down over positions, with a memo:

```python
import functools

def word_break(s, words):
    word_set = set(words)

    @functools.cache
    def can(i):                    # can s[i:] be cut?
        if i == len(s):
            return True
        return any(s[i:j] in word_set and can(j) for j in range(i + 1, len(s) + 1))

    return can(0)
```

The memo is keyed by the **position** `i`, not by the remaining string, as chapter section 3 advises. It recurses up to `len(s)` deep, which is why the test raises the recursion limit to 5000.
