# Longest of any number of words

Write `longest(*words)` that returns the longest of the words passed as separate arguments.

- If several words share the greatest length, return the **first** of them.
- With no arguments, return the empty string `""`.

**Examples**

```python
longest("fig", "banana", "kiwi")     # "banana"
longest("cat", "dog", "emu")         # "cat"     (tie: the first wins)
longest("solo")                      # "solo"
longest()                            # ""
longest(*"the quick brown fox".split())   # "quick"
```
