# Trace a polynomial string hash

A **polynomial hash** turns a string into a number: start with `h = 0` and, for every character, set
`h = (h * B + value) % M`, where `value` is `a = 1, b = 2, ..., z = 26`. Here `B = 31` and `M = 101`, both fixed,
so the output never changes. Predict **exactly** what the program prints. Do not run it.

```python
B = 31
M = 101


def poly(s):
    h = 0
    for ch in s:
        h = (h * B + (ord(ch) - 96)) % M
        print("  after", ch, "h =", h)
    return h


for word in ["abc", "cab", "abd", "zz", "ga"]:
    print(word)
    print("hash", poly(word))
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

Keep `h` in a box. For each letter compute `h * 31 + value`, then take the remainder modulo 101. For example `abc`:
`h = 0 -> (0*31 + 1) % 101 = 1`, then `(1*31 + 2) % 101 = 33`, then `(33*31 + 3) % 101 = 1026 % 101 = 16`
(since `101 * 10 = 1010`).

## After you answer

1. Do `abc` and `cab` have the same hash? What property of the formula makes order matter?
2. Which two different words have the same hash? Why is that unavoidable for a small `M`?
3. After finding a matching hash, what should a program still do before it believes the two strings are equal?
