## Hint 1

Count the letters first (`collections.Counter`). Try `"aabbcc"` by hand: at each step, which letter has the most copies left? Can you place it? If it is the letter you placed last, which letter do you take instead?

## Hint 2

Keep a max-heap of `(-count, letter)` (negative counts, because `heapq` is a min-heap). At every step pop the best letter and append it to the result. The letter you **just placed** must not be placed again right away: do not push it back at once. Keep it aside as `held` and put it back (with its count reduced by one) after the **next** letter has been popped.

## Hint 3

```
heap = [(-count, letter) for each letter]; heapify
held = None                       # the letter placed last, with its remaining count
result = []
while heap:
    count, letter = pop(heap)
    result.append(letter)
    if held is not None and held has copies left: push(heap, held)
    held = (count + 1, letter)    # counts are negative: +1 means one copy used
if len(result) == len(s): return the joined result, else return ""
```

If the heap runs empty while `held` still has copies left, the string cannot be arranged: the result is shorter than `s`.
