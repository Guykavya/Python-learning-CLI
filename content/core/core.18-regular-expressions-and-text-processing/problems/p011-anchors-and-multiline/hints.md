## Hint 1

`"abc\n"` is four characters. Where can `$` match in it without MULTILINE? Where can `\Z` match? And is the newline part of what `fullmatch(r"abc", ...)` must cover?

## Hint 2

Without `re.M`, `^` is only the start of the whole string, so `^\w+` can find just one word in `"one\ntwo\nthree"`. With `re.M`, every line has a start and an end. `\A` and `\Z` ignore the flag.

## Hint 3

```
"abc\n": $ before final \n -> True ; \Z needs the true end -> False
fullmatch must cover the \n -> False ; match + $ -> True (the same $ quirk)
^\w+        no M -> first line only ; with M -> every line
\w+$        no M -> last line only ; with M -> every line
\A, \Z with M -> still first / last only
^t\w* with M -> lines starting with t
"$" on "a\nb\n" (no M): before the final \n, and at the very end -> 2
"^" on "a\nb\n" (M): start, after the 1st \n, after the 2nd \n -> 3
```
