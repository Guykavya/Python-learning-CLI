## Hint 1

To move the largest disc from `source` to `target`, where must all the other n - 1 discs be at that moment?

## Hint 2

Trust the recursion: 'move n - 1 discs from source to spare' is the same problem, smaller, with the pegs' roles swapped.

## Hint 3

```
if n == 0: return []
return (hanoi(n - 1, source, spare, target)       # clear the way
        + [(source, target)]                      # move the largest
        + hanoi(n - 1, spare, target, source))    # put the rest back on top
```
