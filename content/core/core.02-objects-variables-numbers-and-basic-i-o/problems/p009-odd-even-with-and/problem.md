# Odd or even with bitwise AND

Read a whole number `n` (it may be negative). Print three lines:

1. `True` if `n` is odd, otherwise `False`, found with the bitwise AND operator `&`
2. `n` shifted right by one bit (`>>`)
3. `n` shifted left by one bit (`<<`)

**Rule:** use `&` for the odd test. Do not use `%`.

**Example**

Input:
```
7
```
Output:
```
True
3
14
```

**Example 2**

Input:
```
-7
```
Output:
```
True
-4
-14
```
