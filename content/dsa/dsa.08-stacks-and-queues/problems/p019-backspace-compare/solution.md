## Approach

`type_text` is the stack as a text buffer. For the `O(1)` comparison, notice that a backspace only affects characters to its **left**. Reading from the right, we always know how many deletions are still pending, so we can find the last surviving character of each string, compare those two, and step left. Nothing is stored except two indices and two counters.

## Code

```python
def type_text(s):
    buffer = []
    for ch in s:
        if ch == "#":
            if buffer:
                buffer.pop()
        else:
            buffer.append(ch)
    return "".join(buffer)


def next_kept(s, i):
    """Index of the last surviving character at or before i, or -1."""
    skip = 0
    while i >= 0:
        if s[i] == "#":
            skip += 1
        elif skip:
            skip -= 1
        else:
            return i
        i -= 1
    return -1


def backspace_equal(a, b):
    i, j = len(a) - 1, len(b) - 1
    while True:
        i = next_kept(a, i)
        j = next_kept(b, j)
        if i < 0 or j < 0:
            return i < 0 and j < 0
        if a[i] != b[j]:
            return False
        i -= 1
        j -= 1
```

## Complexity

Both are `O(n + m)` time. `type_text` uses `O(n)` memory; `backspace_equal` uses `O(1)`: every index moves left only, and each character is looked at once.

## Another way

`backspace_equal(a, b)` as `type_text(a) == type_text(b)` is the clear, `O(n)`-memory version, and in most programs it is the right choice. The two-pointer version matters when the inputs are huge streams or when memory is tight, and it is a classic interview follow-up.
