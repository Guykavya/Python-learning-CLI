## Hint 1

Do one definition at a time for all three values of `p`. For nearest-rank you need `ceil(p / 100 * 5)`; for inclusive the position `4 * p / 100`; for exclusive `6 * p / 100`.

## Hint 2

For `p = 90`: nearest-rank rank is `ceil(4.5) = 5`; inclusive position is 3.6, so between the 4th and 5th values (40 and 50); exclusive position is 5.4, which is more than n = 5, so the function raises. The `{error}` is printed with the text of the message.
