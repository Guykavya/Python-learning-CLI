## Hint 1

Describe the accepted strings in words, without thinking about the old pattern: a sequence of
words, where every word **except maybe the last** is followed by exactly one whitespace
character, and the last word may also be followed by one. Can a run of letters like `"abc"` be
cut into words in more than one way by your description? It must not.

## Hint 2

Make the whitespace after each repeated word **required**. Then a repetition always ends at a
whitespace character, so the engine has only one way to read each run of letters. The last word
(with no space after it) is handled by a separate piece at the end.

```
SAFE_RE = compile( (?: word-chars+ ONE-whitespace )*  word-chars* )
check: "" yes, "a b " yes, "a  b" no, " a" no
```
