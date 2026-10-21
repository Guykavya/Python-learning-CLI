## Hint 1

Two nested loops: rows outside, seat letters inside. How do you name the seat in row 2,
letter `D`?

## Hint 2

`f"{row}{letter}"` builds `"2D"`. `in` tells you whether it is in the booked list from `split()`.

## Hint 3

Inside the inner loop: if the character is a space, add a space; elif the seat is booked,
add `X`; else add the letter and count it as free. Count every real seat for the total.
