## Hint 1

Write the positions of each block. For a length of 6, `2**k` is 4, so the first block starts at `l = 1` and the second at `r - 4 = 3`.

## Hint 2

For `min`: what is `min(x, x)`? For `+`: what is `x + x`? The property you are looking for says "doing it twice is the same as once".

## Hint 3

For sums: what happens if you use blocks of lengths 4 and 2 (the binary digits of 6) placed one after the other? And what does subtraction allow that `min` does not?
