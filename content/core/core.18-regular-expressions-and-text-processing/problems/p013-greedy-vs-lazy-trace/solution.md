## Walkthrough

1. `<.*>`: the match starts at the first `<`. `.*` swallows the rest of the string, then backs off until the next character is a `>`, which is the **last** `>` in the string. One single match: the whole text.
2. `<.*?>`: `.*?` grows one character at a time and stops at the **first** `>`. Each tag is found separately: `['<b>', '</b>', '<i>', '</i>']`.
3. `<[^>]*>`: `[^>]*` cannot step over a `>`, so it stops at the first one without any backtracking. Same result, and usually the better pattern.
4. `\d{2,4}` is greedy: `1234`.
5. `\d{2,4}?` is lazy: `12`.
6. `findall` greedy: `1234`, then from index 4 the rest `567` (3 digits, within 2 to 4): `['1234', '567']`.
7. `findall` lazy: `12`, `34`, `56`, and the lone `7` cannot make a group of 2: `['12', '34', '56']`.
8. `a.*b` on `"a1b2b3"` runs to the last `b`: `a1b2b`. `a.*?b` stops at the first `b`: `a1b`.
9. `x.*?$`: lazy, but `$` can only match at the end, so `.*?` has to grow to `yz`: `xyz`. Lazy means "as little as **possible**", and here everything is needed.
10. `\w+?` takes one character per match: `['a', 'b', 'c']`.
11. `\s+?` matches one space at a time, so the two spaces are replaced separately: `a__b`.
12. `<(.+?)>` on `"<<a>>"`: the search starts at index 0. `.+?` must take at least one character (`<`), then tries `>` against `a` (fails), grows to `<a`, and now `>` matches. The group is `<a`. Starting at the leftmost position wins over a "nicer" shorter match at index 1.
13. `colou??r` on `"colour color"`: at index 0 the lazy `u??` first skips the `u`, then `r` fails against `u`, so it backtracks and takes the `u`: `colour`. The leftmost match wins; `color` is never reached.
14. `\d+?\d` on `"12345"`: one digit for `\d+?`, one for `\d`: `12`. `\d+?$` must reach the end: `12345`.

## The exact output

```text
['<b>bold</b> and <i>it</i>']
['<b>', '</b>', '<i>', '</i>']
['<b>', '</b>', '<i>', '</i>']
1234
12
['1234', '567']
['12', '34', '56']
a1b2b a1b
xyz
['a', 'b', 'c']
a__b
<a
colour
12 12345
```

**Lesson:** greedy vs lazy only changes the **length** of a match from a given start, never the
start itself (leftmost wins). When you mean "up to the next X", a negated class like `[^X]*`
says it directly and does not backtrack.
