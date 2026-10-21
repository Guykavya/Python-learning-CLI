# Why does the loop give the right answer?

Testing shows a program works on the inputs you tried. An **invariant** lets you argue it works on **every** input.
An invariant is a statement about the variables that is true before the loop starts and stays true after every pass.

**Loop 1: Euclid's algorithm** (with `a` and `b` both whole numbers, `a >= 0`, `b >= 0`, not both 0):

```python
a = int(input())
b = int(input())
while b != 0:
    a, b = b, a % b
print(a)
```

It prints the greatest common divisor of the two numbers that were read. For example 252 and 105 give 21.

**Loop 2: largest so far** (`n >= 1` numbers, each on its own line, any sign):

```python
n = int(input())
largest = int(input())
for k in range(n - 1):
    x = int(input())
    if x > largest:
        largest = x
print(largest)
```

In `answer.md`, answer these questions for **both** loops, in plain words:

1. What stays true before and after every pass (the invariant)? Say it about the original input, not just the variables.
2. Why must the loop stop? (For a `for` loop this is easy; for the `while` loop give a real reason.)
3. Why does "the invariant is still true" plus "the loop has stopped" prove that the printed answer is correct?
4. Someone changes Loop 2 to start with `largest = 0` and to read all `n` numbers inside the loop. For which inputs does
   it now print the wrong answer? Give an example and connect it to the invariant.

For Loop 1 you will need the fact that `gcd(a, b) = gcd(b, a % b)`. Give a short reason why it is true
(hint: `a % b = a - q * b` where `q = a // b`).
