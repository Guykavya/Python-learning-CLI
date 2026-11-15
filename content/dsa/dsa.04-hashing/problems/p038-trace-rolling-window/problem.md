# Trace a rolling hash window

The program hashes every window of three digits in a string as the number the digits spell, modulo 97 (so `B = 10`,
`M = 97`), and updates the hash by **rolling** instead of recomputing. It also prints the direct value `int(window) % 97` so you can see
that both agree. Predict **exactly** what it prints. Do not run it.

```python
s = "31415926"
k = 3
B = 10
M = 97
top = pow(B, k - 1, M)
print("top", top)
h = 0
for ch in s[:k]:
    h = (h * B + int(ch)) % M
print("first", s[:k], h)
for i in range(k, len(s)):
    h = ((h - int(s[i - k]) * top) * B + int(s[i])) % M
    window = s[i - k + 1:i + 1]
    print(window, h, int(window) % M, h == int(window) % M)
```

Write your answer in `answer.txt`, one line per printed line. Booleans print as `True` or `False`.

## How to work

`top = 10^2 % 97 = 3`. The first hash is the value of `314` modulo 97. For each step the **leaving** digit `d` is removed with
`h - d * top`, the result is multiplied by 10, and the **entering** digit is added; then take `% 97`. Python's `%` gives a
non-negative result even if the intermediate number is negative.

## After you answer

1. Why does the leaving digit have weight `top = B^(k-1) mod M`?
2. Does the rolling value always equal the direct one? Why is that not a coincidence?
3. How many multiplications does one slide cost, and how many would recomputing the window cost?
