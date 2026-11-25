## Hint 1

The condition number of this matrix is about `4 / eps`. For `eps = 1e-10`, how many zeros is that? A double has about 16 digits.

## Hint 2

Think about the singular values of `A^T A`: they are the **squares** of the singular values of `A`. What happens to the ratio of the largest to the smallest?
