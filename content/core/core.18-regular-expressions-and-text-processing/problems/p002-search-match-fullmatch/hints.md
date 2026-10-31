## Hint 1

For each text in the loop, ask three questions. Does `cat` appear anywhere? Does the text **start** with `cat`? Is the text **exactly** `cat`? A "no" prints `None`.

## Hint 2

`\d+` is "one or more digits" and takes as many as it can. `re.match(r"\d+", "42abc")` succeeds with `42`, but `fullmatch` needs the digits to run to the very end. `re.search` stops at the **first** run of digits, it does not look for the longest one.

## Hint 3

```
loop: text, then search / match / fullmatch results
"42abc": match -> 42, fullmatch -> None
"ab12cd345": search -> first run, match -> position 0 is a letter
"ca." : dot is any one char -> "cat" ok, "cart" is 4 chars -> None
r"" matches "" at 0 -> Match object (truthy), group() is ""
"foo boo": first "o" at index 1; "boo" spans 4..7
```
