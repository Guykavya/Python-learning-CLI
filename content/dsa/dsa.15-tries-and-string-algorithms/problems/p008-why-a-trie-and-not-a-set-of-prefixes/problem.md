# Explain: why a trie and not a set of prefixes?

A classmate says: "Tries are pointless in Python. For `starts_with`, I put **every prefix of every word** into one `set`, and the words themselves into a second `set`. Both lookups are `O(1)`."

```python
class PrefixSets:
    def __init__(self):
        self.words = set()
        self.prefixes = set()

    def insert(self, word):
        self.words.add(word)
        for k in range(len(word) + 1):
            self.prefixes.add(word[:k])

    def search(self, word):
        return word in self.words

    def starts_with(self, prefix):
        return prefix in self.prefixes
```

It gives the same answers as the trie of p001. Write a short explanation (8 to 12 sentences) in `answer.md` that answers:

1. **Is a set lookup really `O(1)` here?** What must Python do with the string `prefix` before it can look it up?
2. **Insert cost.** How many characters does `insert` copy for a word of length `L`? Compare with the trie.
3. **Memory.** For one word of length `L`, how many characters do the stored prefixes hold in total? Work it out for `L = 10` and for 10**5 words of length 10 that share no prefixes. How many trie nodes would those words need at most?
4. **Questions the sets cannot answer cheaply.** Name two operations from this module that are easy with a trie and hard with `PrefixSets` (think of autocomplete, counts, deletion, the shortest root of p007, wildcards).
5. **When is the classmate right?** Give one situation where the sets (or a sorted list) are the better choice.

Then compare with the model answer and rate yourself.
