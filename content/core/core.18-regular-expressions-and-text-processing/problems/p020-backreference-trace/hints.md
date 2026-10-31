## Hint 1

For the quote loop: when group 1 is `"`, the lazy `.*?` stops at the first **`"`**, not at the
first quote of any kind. So what happens to the apostrophe in `it's`? What does `print` show
for `m.group(1)` (the quote character itself, without extra quotes)?

## Hint 2

For `(\w)\1` walk through `bookkeeper` and list every place where a letter is directly followed
by the same letter. For `(\w)\1+` the whole run of equal letters is replaced by one copy.

## Hint 3

For the tag search: at `<b>` group 1 is `b`, and the pattern needs `</b>` later. Is there one?
If not, the search moves on. Where does the first `<` that is followed by a word start? Count
the characters to get `m.start()`. For the last line: what does the normal string `"(a)\1"`
actually contain?
