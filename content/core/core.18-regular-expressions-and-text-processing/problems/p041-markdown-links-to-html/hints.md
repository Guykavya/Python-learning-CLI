## Hint 1

Write the pattern in three parts: the `[text]`, the `(url)` right after it, and a condition that
there is no `!` just before the `[`. How do you say "any characters except `]`" without the
greedy `.*` running past the end of the first link?

## Hint 2

Two capturing groups, and a replacement string that uses them with `\1` and `\2`. A negative
lookbehind checks the character before without consuming it.

```
LINK = (?<!!)  \[  ( not-] chars, 1+ )  \]  \(  ( not-) and not-space chars, 1+ )  \)
return LINK.sub('<a href="\2">\1</a>', text)
```
