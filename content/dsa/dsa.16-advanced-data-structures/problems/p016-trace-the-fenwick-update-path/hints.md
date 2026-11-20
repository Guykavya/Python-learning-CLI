## Hint 1

`11 = 1011`: the lowest bit is 1, so the next cell is `12 = 1100`; its lowest bit is 4, so the next is `16 = 10000`; then `32 > 16`: stop.

## Hint 2

`15 = 1111`: remove the lowest bit to get `14 = 1110`, then `12 = 1100`, then `8 = 1000`, then 0: stop. The printed binary has no leading zeros (`f"{p:b}"`).

## Hint 3

Cell 6 covers `5..6`, cell 8 covers `1..8`, cell 16 covers `1..16`. Is there any other cell whose block contains 6? (Cell 7 covers only 7; cell 12 covers `9..12`.)
