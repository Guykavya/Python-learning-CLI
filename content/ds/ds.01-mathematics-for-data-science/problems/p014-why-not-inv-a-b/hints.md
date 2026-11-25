## Hint 1

To get `x` you need one vector, but the inverse is a whole `n x n` matrix. Roughly how many linear solves is that?

## Hint 2

A factorisation (LU) of `A` is the expensive part. Once you have it, solving for a new `b` is cheap. Which of the two approaches lets you keep it?
