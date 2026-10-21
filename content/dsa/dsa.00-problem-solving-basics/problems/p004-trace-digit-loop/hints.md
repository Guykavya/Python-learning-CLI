## Hint 1

For the first loop, what are `5207 % 10` and `5207 // 10`? Write both down before moving on.

## Hint 2

`print` happens at the end of each iteration, after `n` has already been shortened. So the "left" value on each line is the number *after* removing the digit. The `done` line prints only once, after the loop.

## Hint 3

In the second loop, the `if` checks the last digit *before* `m` is shortened, but `print` runs *after*. So the first line shows `100`, not `1000`. Count how many times `m % 10 == 0` is true while `m` takes the values 1000, 100, 10, 1.
