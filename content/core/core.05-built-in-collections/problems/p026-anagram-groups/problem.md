# Anagram groups

Two words are **anagrams** if they use exactly the same letters, like `listen` and `silent`.
Read one line of lowercase words and group the anagrams together. Print one group per line,
words separated by spaces.

- Groups appear in the order their first word appears.
- Inside a group, words keep their input order.
- If the exact same word appears more than once, list it only once.
- Print `No words.` for an empty line.

**Example**

Input:
```
listen enlist google silent tinsel elgoog cat act listen
```
Output:
```
listen enlist silent tinsel
google elgoog
cat act
```
