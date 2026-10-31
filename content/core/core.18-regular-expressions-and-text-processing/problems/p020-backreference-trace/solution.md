## Approach

For each backreference, first find what the group captured, then look for that exact text.

## Line by line

1. The loop finds `"hi"` (group 1 is `"`), then `'yo'` (group 1 is `'`), then `"it's"`: group 1
   is `"`, so the `'` inside does not end it. `print` shows the quote and the inner text.
2. `bookkeeper`: `oo`, `kk`, `ee` give `['o', 'k', 'e']`.
3. `(\w)\1+` replaces each run of a repeated letter by one copy: `aaa`→`a`, `cc`→`c`, `dddd`→`d`.
   Result `abcd`.
4. `12-12`: `\1` must be `12` again, `True`. `12-123`: `\1` matches `12` but then `3` is left
   over and fullmatch fails. No other split works (group 1 must be the whole part before `-`).
   `False`.
5. `'mixed"`: the closing quote must equal the opening one (`'`), it is `"`: `None`. `'same'`
   matches, group `q` is `'`.
6. At `<b>`, group 1 is `b` and `</b>` never appears, so the engine moves on. `</i>` cannot
   start a match (`/` is not `\w`). At `<i>` it finds `</i>`: the match is `<i>it</i>`, starting
   at index 12 (`<b>bold</i> ` is 12 characters).
7. With IGNORECASE, `\1` = `a` also matches `A`, so the match is `aA`.
8. `"(a)\1"` (not raw) contains the character `\x01`, so it looks for `a` followed by that
   character: no match in `"aa"`, `[]`. The raw version finds `aa`: `['a']`.

## Expected output

```
" hi
' yo
" it's
['o', 'k', 'e']
abcd
True False
None '
<i>it</i> 12
aA
[] ['a']
```

## Complexity

The lazy `.*?` with a backreference retries the closing check at each step, so the quote loop
is O(n²) in the worst case; fine for short text.

## Another way

For the quotes you could write two alternatives, `"[^"]*"|'[^']*'`. It is faster (no
backtracking), but you then need two groups for the inside text. The backreference keeps one
group for both cases.
