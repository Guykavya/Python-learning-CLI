## Approach

Clean the text into a deque of lower-case letters and digits. Each step removes one character from each end and compares them. The first pair that differs is the answer; if the deque shrinks to 0 or 1 characters with no mismatch, it is a palindrome.

## Code

```python
from collections import deque


def first_mismatch(text):
    d = deque(ch.lower() for ch in text if ch.isalnum())
    while len(d) > 1:
        left = d.popleft()
        right = d.pop()
        if left != right:
            return (left, right)
    return None
```

## Complexity

`O(n)` time: building the deque is one pass, and every character is removed at most once with an `O(1)` operation. `O(n)` memory for the deque.

## Another way

Two indices on a cleaned string do the same without removing anything:

```python
def first_mismatch(text):
    s = [ch.lower() for ch in text if ch.isalnum()]
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return (s[i], s[j])
        i += 1
        j -= 1
    return None
```

This is the two-pointer pattern from dsa.03. The deque version makes the "both ends" idea visible.
