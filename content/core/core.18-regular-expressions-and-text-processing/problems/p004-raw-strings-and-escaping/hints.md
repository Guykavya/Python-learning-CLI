## Hint 1

Count characters. `"\n"` is one character; `r"\n"` is a backslash and an `n`. `"C:\\new"` is `C`, `:`, one backslash, `n`, `e`, `w`. How many is that, and how many does `r"C:\new"` have?

## Hint 2

For the two `re.search` lines, first work out the **string** Python builds, then ask what the regex engine does with it. `"\\d"` builds the two characters `\d`. `r"\\d"` builds three characters `\\d`: to the engine that is "a literal backslash, then `d`". And `"\bcat"` (not raw) contains a backspace character, not a word boundary.

## Hint 3

```
len: 1 2 | repr: '\t' '\\t' | len: 6 6 | equal: True
escape: + . * and space get a backslash; = and _ do not
"\\d" -> engine sees \d -> digit -> True ; r"\\d" -> literal "\d" -> False
r"\." -> only dots ; "." -> every char
r"\bcat" -> boundary -> cat ; "\bcat" -> backspace+cat -> None
escape("2.5") matches only "2.5"; plain "2.5" matches 2?5 three times
```
