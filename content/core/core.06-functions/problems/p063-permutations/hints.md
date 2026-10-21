## Hint 1

Choose which item goes first. What remains is a smaller list. How do you get 'the list without the item at index i'?

## Hint 2

`rest = items[:i] + items[i + 1:]` builds a new list without position i, leaving `items` unchanged.

## Hint 3

```
if not items: return [[]]
result = []
for i in range(len(items)):
    rest = items[:i] + items[i + 1:]
    for p in permutations(rest):
        result.append([items[i]] + p)
return result

anagrams: set of "".join(p) for p in permutations(list(word)), then sorted
```
