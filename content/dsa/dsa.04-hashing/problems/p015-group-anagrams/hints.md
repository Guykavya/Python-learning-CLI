## Hint 1

Two words are anagrams exactly when something about them is equal. What single value could you compute for each word that is the same for all its anagrams?

## Hint 2

`key = "".join(sorted(word))`. Use a dictionary from key to a list of words. Append each word to its key's list.

## Hint 3

```
groups = {}
for w in words:
    groups.setdefault(key(w), []).append(w)
sort each group; sort the groups by group[0]; print
```
