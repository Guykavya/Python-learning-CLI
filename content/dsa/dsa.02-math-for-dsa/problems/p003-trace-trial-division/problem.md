# Trace trial division

This function tests whether `n` is prime and prints what it does at each step. Predict **exactly** what the
program prints for the five numbers. Do not run it.

```python
def check(n):
    i = 2
    while i * i <= n:
        print("try", i, "on", n)
        if n % i == 0:
            print(n, "is divisible by", i)
            return False
        i += 1
    print("no divisor found for", n)
    return True


for n in [1, 2, 9, 17, 30]:
    print("--", n)
    result = check(n)
    print("prime" if result and n > 1 else "not prime")
```

Write your answer in `answer.txt`, one line per printed line.

## Things to watch

- For which `n` does the `while` body not run at all?
- How many tries does a prime like 17 need? What is the last `i` that is tried, and why does the loop stop there?
- What does the function return for 1, and why does the last `print` still say `not prime`?

## After you answer

Count the lines `try ...` for 17. Now think of `n = 10^9 + 7`: about how many `try` lines would it print?
