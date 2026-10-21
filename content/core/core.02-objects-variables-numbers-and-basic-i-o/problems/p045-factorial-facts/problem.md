# Facts about a huge factorial

Read a whole number `n` from 0 to 3000. Print two facts about `n!` (`math.factorial(n)`):

```
Digits: <how many decimal digits n! has>
Trailing zeros: <how many zeros n! ends with>
```

**Rules:**

- You have not learned loops. Use maths, not counting.
- Do not convert the factorial to a string. (Try `print(math.factorial(3000))` once to see why:
  Python refuses to turn an int with more than 4300 digits into text by default.)

**Example**

Input:
```
10
```
Output:
```
Digits: 7
Trailing zeros: 2
```

`10! = 3628800`: 7 digits, 2 trailing zeros.

**Maths you need**

- A positive whole number `x` has `floor(log10(x)) + 1` digits. `math.log10` accepts huge ints.
- Each trailing zero comes from a factor 10 = 2 x 5. There are always more 2s than 5s, so count the
  factors of 5 in `1 x 2 x ... x n`: `n // 5 + n // 25 + n // 125 + n // 625 + ...`
  (stop when the power of 5 is larger than `n`; for `n <= 3000`, 625 is the largest needed).
