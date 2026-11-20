# Reorganise a string

Given a string `s` of lowercase letters, rearrange its letters so that **no two equal letters are next to each other**. Write `reorganize(s)`, which returns **any** such arrangement, or the empty string `""` if there is none. The result must use exactly the letters of `s` (same letters, same counts). For `s = ""` the answer is `""`.

The tests do not look for one particular answer: they check that your result is made of the same letters and that no two neighbours are equal.

## Example

```python
>>> reorganize("aab")
'aba'
>>> reorganize("aaab")             # impossible: three a's need at least two letters between them
''
>>> reorganize("aabbcc")           # one valid answer is 'abcabc'; others like 'acbacb' are also fine
'abcabc'
>>> reorganize("")
''
```

## Constraints

- `len(s)` up to 100,001. The big tests run in a separate process with a 10-second limit.
- An arrangement exists exactly when the most frequent letter appears at most `(len(s) + 1) // 2` times. The tests also check small strings against a search over **all** orderings, so your function must not return `""` when an arrangement exists.

## Think about

Which letter is the most dangerous: the one that has the most copies left. If you always place the letter with the most copies left, what stops you from placing the same letter twice in a row? Where does the letter that you just placed wait, and when does it come back?
