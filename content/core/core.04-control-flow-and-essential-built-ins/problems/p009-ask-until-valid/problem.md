# Ask until valid

Keep reading lines until one is a whole number from **1 to 10** (spaces around it are fine).

- For each line that is not valid, print `Invalid: <the line, stripped>`.
- When a valid line arrives, print `Accepted <number> after <k> attempts`, where `k` counts
  every line read, including the valid one. Use `attempt` (singular) when `k` is 1.

Do not use `try`/`except`. Use `str.isdigit()` to check that the text is made of digits
before converting it.

**Example**

Input:
```
ten
0
 7
```
Output:
```
Invalid: ten
Invalid: 0
Accepted 7 after 3 attempts
```

The input always contains a valid line eventually.
