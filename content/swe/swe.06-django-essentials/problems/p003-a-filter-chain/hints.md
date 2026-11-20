## Hint 1

Go through the templates one at a time and write the value of the variable first. For each filter ask: what goes in, what comes out? Remember that the output is only the text between the brackets.

## Hint 2

`default` replaces any **false** value: `0`, `""`, `[]`, `None` and a missing variable. `truncatechars:8` keeps 7 characters and adds one `…`, so the total is 8. A missing variable inside `{{ }}` gives an empty string. Without `|safe`, Django escapes `<`, `>`, `&`, `'` and `"` in every variable.

## Hint 3

```text
1  count=0 is false             -> default gives "none"
2  "hello world" -> "HELLO WORLD" -> first 7 chars "HELLO W" + "…"
3  date(2026,3,9) with Y-m-d     -> 2026-03-09
4  length of the list is 3       -> "3 items"
5  missing                       -> ""
6  escaped: &lt;b&gt;hi&lt;/b&gt;   safe: <b>hi</b>
```
