# Anagram check

Two phrases are **anagrams** if one uses exactly the same letters as the other, ignoring spaces, punctuation and case. "Dormitory" and "Dirty room!" are anagrams.

Read two lines. For each, compute its **key**: casefold it, remove all whitespace and ASCII punctuation, then sort the characters and join them back into a string. Print:

```
Key 1: <key of the first line>
Key 2: <key of the second line>
Anagrams: <True or False>
```

**Example**

Input:
```
Dormitory
Dirty room!
```
Output:
```
Key 1: dimoorrty
Key 2: dimoorrty
Anagrams: True
```

`sorted("cab")` is a new built-in for you: it returns the characters in order as a list, `['a', 'b', 'c']`. Join it with `"".join(...)` to get `"abc"`.
