# Alien dictionary

An alien language uses lowercase English letters, but in an unknown alphabetical order. You get a list `words` that is **sorted** in the alien dictionary order.

Write `alien_order(words)`. Return a string that contains **every letter that appears in the words, exactly once**, in an order that is consistent with the sorted list. If several orders are consistent, return any of them (the tests check your string). If **no** order is consistent, return `""`.

This is chapter section 18, example 3. What the sorted list tells you:

- Only **neighbouring** words carry information. Compare `words[i]` with `words[i + 1]`: at the **first** position where they differ, the letter of `words[i]` comes before the letter of `words[i + 1]`. That is one edge. The letters **after** that position tell you nothing.
- If the words never differ and the **first** word is **longer** (`"abc"` before `"ab"`), the list cannot be sorted in any alphabet: return `""`.
- The edges can form a cycle (`a` before `b` and `b` before `a`): return `""`.
- A letter that appears in no edge still belongs in the answer, anywhere.

## Example

```python
>>> alien_order(["wrt", "wrf", "er", "ett", "rftt"])
'wertf'
>>> alien_order(["z", "x"])
'zx'
>>> alien_order(["z", "x", "z"])          # z < x and x < z: a cycle
''
>>> alien_order(["abc", "ab"])            # a longer word before its own prefix
''
>>> alien_order(["ab", "abc"])            # fine: the prefix comes first
'abc'                                     # any order of a, b, c is correct here
```

In the first example the neighbouring pairs give `t < f` (wr**t** / wr**f**), `w < e` (**w**rf / **e**r), `r < t` (e**r** / e**t**t) and `e < r` (**e**tt / **r**ftt). One order that respects all four is `w e r t f`.

## Constraints

- `1 <= len(words) <= 1000`, each word has 1 to 100 lowercase letters.

## Think about

Why is it wrong to add an edge for **every** position where two neighbouring words differ? Make an example where that would invent a cycle.
