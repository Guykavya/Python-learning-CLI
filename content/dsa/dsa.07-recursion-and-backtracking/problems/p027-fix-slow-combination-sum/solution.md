## Approach

The starter explores a child for every candidate and lets the child discover that it overshot. Those children are dead leaves: with many large candidates they make up most of the tree. Checking **before** the call removes them. Sorting first makes the check a `break`, which also saves the loop iterations over the remaining (larger) candidates.

## Code

```python
def combination_sum(candidates, target, counter):
    candidates = sorted(candidates)
    result, path = [], []

    def go(start, remaining):
        counter.tick()                 # keep this line: the tests count the calls
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break                  # sorted: every later candidate is too big as well
            path.append(c)
            go(i, remaining - c)
            path.pop()

    go(0, target)
    return result
```

## Complexity

The number of calls drops from (answers and partial sums) x (number of candidates) to roughly the number of partial sums that still fit: 207,884 to 11,937 calls in the big test. The worst case stays exponential; pruning removes dead branches, not answers.

## Another way

Without sorting, `if candidates[i] > remaining: continue` makes exactly the same calls (the tests count calls), but the loop keeps checking every larger candidate one by one. Sorting plus `break` is the version that also scales when there are many candidates.
