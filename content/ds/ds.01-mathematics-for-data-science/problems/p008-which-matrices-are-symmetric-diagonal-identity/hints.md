## Hint 1

Check the labels in the order the code does: identity first, then diagonal, then symmetric. Which test does the first matrix pass?

## Hint 2

The all-zero matrix equals its own `np.diag(np.diag(M))`, so it is a diagonal matrix (and also symmetric): the first test it passes is "diagonal".
