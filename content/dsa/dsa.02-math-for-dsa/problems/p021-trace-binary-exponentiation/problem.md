# Trace binary exponentiation

Fast exponentiation squares the base and halves the exponent. Here it prints its state at the **top of every
pass** of the loop: `base exp result`. Predict **exactly** what the program prints. Do not run it.

```python
def power(base, exp, mod):
    result = 1
    base = base % mod
    while exp > 0:
        print(base, exp, result)
        if exp & 1:
            result = result * base % mod
        base = base * base % mod
        exp = exp >> 1
    return result


print("answer", power(3, 13, 1000))
print("answer", power(2, 10, 1000))
print("answer", power(7, 0, 5))
print("answer", power(10, 5, 1))
```

Write your answer in `answer.txt`, one line per printed line. The lines look like `9 6 3`.

## How to work

Keep a small table with the columns `base`, `exp`, `result` and fill one row per pass. For each row decide:
is the lowest bit of `exp` set (`exp & 1`)? If yes, `result` is multiplied by `base`. Then `base` is squared and
`exp` is halved (rounded down). All multiplications are taken modulo `mod`, so `3^13 = 1594323` never appears:
only the remainders do.

## After you answer

1. Write 13 in binary. Which passes multiplied `result`? Do they match the 1 bits of 13?
2. How many passes ran for `exp = 13` and for `exp = 10`? Compare with `exp.bit_length()`.
3. Why does `power(7, 0, 5)` print no state line at all, and why is the answer 1?
4. Why is the answer to the last call 0, and what is `base` when it starts?
