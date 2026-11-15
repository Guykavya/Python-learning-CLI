## Hint 1

Level `i` of the tree chooses a letter for `digits[i]`. The answer is complete when every digit has a letter.

## Hint 2

Keep a `PHONE` dictionary from digit to letters. `go(i)`: if `i == len(digits)`, record `"".join(path)`; otherwise loop over `PHONE[digits[i]]`, append, recurse with `i + 1`, pop.

## Hint 3

Handle the empty input before starting the recursion: `if not digits: return []`.
