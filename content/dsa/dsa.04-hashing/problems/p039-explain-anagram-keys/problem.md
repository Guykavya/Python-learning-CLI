# Explain: choosing a grouping key

To group anagrams you need a key that is **equal for all anagrams and different for everything else**. Four candidates for a word `w`:

```python
key1 = "".join(sorted(w))                       # sorted letters
key2 = tuple(w.count(c) for c in "abcdefghijklmnopqrstuvwxyz")   # 26 counts
key3 = sum(ord(c) for c in w)                   # sum of letter codes
key4 = frozenset(w)                             # set of letters
```

Answer in `answer.md`, in your own words, with small examples. Aim for 250 to 400 words.

1. **Which are correct?** For each key, say if it is correct (anagrams and only anagrams share it). For each wrong one, give a pair of words that breaks it.
2. **Hashable.** Why is `sorted(w)` itself (a list) not usable as a key, but `"".join(sorted(w))` is?
3. **Cost.** Give the time per word for `key1` and `key2` in terms of the word length `L` (and the alphabet size, for `key2`). When is `key2` better, and when `key1`?
4. **Rolling to large alphabets.** The words use any Unicode character (thousands of possible letters). What key would you use instead of the
   26-count tuple?
5. **Using the idea elsewhere.** Which other problem in this module is also "map every item to a canonical form and group by it"? Name one.

Then read `solution.md` and `answer.md`, and rate your answer.
