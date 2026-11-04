## Hint 1

First hash: `3`, then `3*10+1 = 31`, then `31*10+4 = 314`, and `314 % 97 = 23` (97 * 3 = 291).

## Hint 2

Step for `i = 3` (entering digit 1, leaving digit 3): `h = ((23 - 3*3) * 10 + 1) % 97 = (14 * 10 + 1) % 97 = 141 % 97 = 44`. The window is `141` and `141 % 97 = 44`.

## Hint 3

Keep going window by window: `415`, `159`, `592`, `926`. Each time compute the rolling value and the direct value; they match.
