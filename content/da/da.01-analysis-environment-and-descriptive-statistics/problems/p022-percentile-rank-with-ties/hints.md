## Hint 1

There are 8 marks. For each score count how many marks are strictly smaller (`below`) and how many are exactly equal (`equal`). The rank is `100 * (below + equal / 2) / 8`.

## Hint 2

For 70: `below` is 3 (50, 60, 60) and `equal` is 3, so `(3 + 1.5) / 8 * 100 = 56.25`. The format `.1f` rounds a number that is exactly halfway to the even digit.
