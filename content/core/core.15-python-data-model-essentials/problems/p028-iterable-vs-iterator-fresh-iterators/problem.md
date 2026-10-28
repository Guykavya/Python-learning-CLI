# Explain: iterable vs iterator

Dev wrote two classes that look almost the same and found one of them acts strangely:

```python
class CountDown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1


class Range3:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        k = self.n
        while k > 0:
            yield k
            k -= 1


c = CountDown(3)
print(list(c))     # [3, 2, 1]
print(list(c))     # []        <- surprise!
r = Range3(3)
print(list(r))     # [3, 2, 1]
print(list(r))     # [3, 2, 1]
```

"Both count down, so why does `c` run dry?"

In `answer.md` (about 150 to 300 words), explain:

1. What an **iterable** and an **iterator** are, and the methods each one needs. What does a `for` loop do with them?
2. Exactly why `list(c)` is empty the second time.
3. Why `Range3` can be listed over and over.
4. How to change `CountDown` so it can be listed twice (describe or write the small change).
5. Which design is right for a container-like class and which one for a one-shot stream, and why.

## Example of the level of detail

"A `for` loop first calls `iter(obj)`, then repeatedly calls `next()` on the result." A good answer goes on
like this for each point.
