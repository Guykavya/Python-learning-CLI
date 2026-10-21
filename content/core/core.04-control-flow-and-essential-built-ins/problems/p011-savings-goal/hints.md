## Hint 1

You do not know the number of months in advance. Which loop keeps going while a condition holds?

## Hint 2

The loop condition is "balance is still below the goal". What happens to that condition if
nothing is ever added?

## Hint 3

Check the two special cases before the loop. Inside: `balance += balance * rate / 100`,
`balance += deposit`, `months += 1`.
