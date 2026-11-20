# Matrix chain multiplication

You must multiply a chain of matrices `A0 A1 ... A(n-1)`. Matrix `i` has size `dims[i] x dims[i + 1]`, so `dims` has `n + 1` numbers. Multiplying a `p x q` matrix by a `q x r` matrix costs `p * q * r` scalar multiplications. The **result** does not depend on the bracketing, but the **cost** does (chapter section 17).

Write `matrix_chain_cost(dims)` that returns the **smallest** total cost over all bracketings.

## Example

```python
>>> matrix_chain_cost([10, 30, 5, 60])       # (A0 A1) A2 = 1500 + 3000
4500
>>> matrix_chain_cost([40, 20, 30, 10, 30])
26000
>>> matrix_chain_cost([5, 10, 3, 12, 5])     # (A0 A1)(A2 A3) = 150 + 180 + 75
405
>>> matrix_chain_cost([7, 3])                # one matrix: nothing to multiply
0
```

## Constraints

- `2 <= len(dims) <= 151` (1 to 150 matrices), `1 <= dims[i] <= 100`.
- `O(n^3)` time. The number of bracketings of 150 matrices has more than 80 digits: a recursion without a memo cannot try them all.

## Think about

Any bracketing has a **last** multiplication: `(A_i ... A_k)` times `(A_(k+1) ... A_j)`. What are the sizes of those two products, so what does the last step cost? And in which order must you fill `f[i][j]` so that `f[i][k]` and `f[k + 1][j]` are ready?
