# One print with the walrus

Read a whole number `n`. Print **one line** with these four values separated by ` | `:

1. `n`
2. `n` squared
3. the square modulo 7
4. `True` if the square is greater than 100, else `False`

**Rules** (this is a puzzle about the walrus operator `:=`):

- Your program must contain **no ordinary assignment statements** (no `=` statement at all).
- It must contain **exactly one** `print` call.
- Compute the square only once: store it with `:=` and reuse it.

**Example**

Input:
```
12
```
Output:
```
12 | 144 | 4 | True
```
