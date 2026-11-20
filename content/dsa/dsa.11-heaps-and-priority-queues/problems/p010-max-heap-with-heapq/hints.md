## Hint 1

Keep one list `self._h` that holds `-x` for every item `x`. The smallest negative number is the largest original number, so `self._h[0]` is the root. Which of your five methods must **negate** a number before the number goes into the list, and which must negate it **back** when it comes out?

## Hint 2

Going in: the constructor and `push`. Coming out: `pop` and `peek`. The constructor builds a **new** list with `[-x for x in items]` and calls `heapq.heapify` on it; this also copies the input, so the caller's list does not change. The error for an empty heap comes for free from `heappop` on `[]` and from `self._h[0]`, both raise `IndexError`.

## Hint 3

```
__init__(items):  self._h = [-x for x in items];  heapq.heapify(self._h)
push(x):          heapq.heappush(self._h, -x)
pop():            return -heapq.heappop(self._h)
peek():           return -self._h[0]
__len__():        return len(self._h)
```
