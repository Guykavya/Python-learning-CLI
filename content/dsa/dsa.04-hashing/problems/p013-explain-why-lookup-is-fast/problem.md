# Explain: why is a hash lookup fast?

A program checks `x in items` for 100000 different values of `x`. Compare two choices:

```python
items = list(range(100000))      # a list
items = set(range(100000))       # a set
```

Answer in `answer.md`, in your own words, with small numbers where they help. Aim for 150 to 300 words.

1. **List cost.** How many comparisons does one failed `x in items` do on the list? Roughly how many for all
   100000 checks?
2. **Set cost.** In one or two sentences, how does a set find `x` **without** looking at every item? Use the words
   "hash" and "bucket" (or "slot").
3. **Average vs worst.** The set is called O(1) *on average*. What can make one lookup slow, and how likely is it
   with a good hash function?
4. **The price.** Name two costs of the set compared with the list (think of memory and of what it cannot do).
5. **Requirement.** What property must a value have to be put in a set, and why does the set need it?

Then read `solution.md` and `answer.md`, and rate your answer.
