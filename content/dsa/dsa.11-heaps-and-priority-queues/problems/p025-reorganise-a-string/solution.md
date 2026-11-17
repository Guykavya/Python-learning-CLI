## Approach

Greedy: at each step place the letter that has the **most copies left**, except the letter that was placed in the previous step. The most frequent letter is the one that is hardest to separate, so it should be used as early as it is allowed. A max-heap of `(-count, letter)` gives that letter.

The letter just placed waits for one round: it is kept in a variable `held` and goes back into the heap after the next letter has been taken, with its count reduced by one.

If the heap becomes empty while `held` still has copies, no other letter is available to stand between them: the string cannot be reorganised, and the result is shorter than `s`; return `""`.

## Code

```python
import heapq
from collections import Counter

def reorganize(s):
    heap = [(-count, letter) for letter, count in Counter(s).items()]
    heapq.heapify(heap)
    result = []
    held = (0, "")                                   # the letter placed last, not yet back in the heap
    while heap:
        count, letter = heapq.heappop(heap)
        result.append(letter)
        if held[0] < 0:
            heapq.heappush(heap, held)               # the previous letter may be used again
        held = (count + 1, letter)                   # one copy used (counts are negative)
    return "".join(result) if len(result) == len(s) else ""
```

## Complexity

`O(n log a)` time for `n` letters and `a` different letters (at most 26 here), `O(a)` memory besides the result.

## Another way

**Fill by position.** An arrangement exists exactly when the most frequent letter appears at most `(n + 1) // 2` times (otherwise return `""` at once). Then sort the letters so that the most frequent letter comes first, with all copies of a letter together (`aaabbc`), and write them into the positions `0, 2, 4, ...` and then `1, 3, 5, ...`. Equal letters are never neighbours: a letter could touch itself only if it took an even slot and the odd slot next to it, which needs about half of all slots; only the most frequent letter can have that many, and it is written first, from position 0. This needs no heap, only a sort of the 26 counts.
