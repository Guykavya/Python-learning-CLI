## Hint 1

Count first: `collections.Counter(words)` gives `word -> count`. Now you need the `k` best entries. A tuple `(-count, word)` sorts the way the answer is ordered: the biggest count has the smallest `-count`, and for equal counts the words compare alphabetically. So "the `k` best" means "the `k` smallest tuples `(-count, word)`".

## Hint 2

You can keep the `k` best with a heap, or let `heapq.nsmallest(k, counts.items(), key=...)` do it. With `nsmallest` the key is a function of one `(word, count)` pair: it must return `(-count, word)`. Return only the words at the end. Check `k <= 0` yourself, and remember that `nsmallest` with `k` larger than the number of items just returns all of them.

## Hint 3

```
counts = Counter(words)
best = nsmallest(k, counts.items(), key = lambda pair: (-pair[1], pair[0]))
return [word for word, count in best]
(with k <= 0 -> [])
```
