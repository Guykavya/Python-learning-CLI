# Fix the naive search

A log-analysis tool counts where an error code appears in huge log files. Its search, in `starter.py`, gives correct answers, but on some files it never finishes:

```python
def find_all(text, pattern):
    """All start positions of pattern in text, overlapping ones included. pattern is not empty."""
    n, m = len(text), len(pattern)
    found = []
    for start in range(n - m + 1):
        k = 0
        while k < m and text[start + k] == pattern[k]:
            k += 1
        if k == m:
            found.append(start)
    return found
```

1. Find the input that makes it slow (chapter section 1, "The slowness we want to remove") and explain in a comment at the top of `solution.py` why it costs `O(n * m)` there.
2. Rewrite `find_all` with KMP so that it runs in `O(n + m)` and returns exactly the same lists.

Keep the function name and the behaviour: overlapping matches are included, and `pattern` is never empty.

## Example

```python
>>> find_all("abcabcabc", "cab")
[2, 5]
>>> find_all("aaaa", "aa")
[0, 1, 2]
>>> find_all("ab", "abc")
[]
```

## Constraints

- Texts up to 10**6 characters, patterns up to 10**4. The tests time a log line made of 10**6 `a`s searched for `aaa...ab`.

## Think about

1. On a text of `a`s and the pattern `a...ab`, how many comparisons does the inner loop make at each start? How many starts are there?
2. What does the naive search forget after a mismatch that KMP remembers?
