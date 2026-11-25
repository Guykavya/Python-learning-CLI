## Approach

`sqrt(25) = 5`, `sqrt(100) = 10`, `sqrt(400) = 20`, `sqrt(1600) = 40`, so the SEs are 4.00, 2.00, 1.00, 0.50. Each step multiplies n by 4 and halves the SE. The last line prints `4`.

## Check

Run the program and compare.

## Another way

For a given SE target, solve `n = (sd / SE)^2`: that is the sample-size formula of problem 16.
