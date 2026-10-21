# Three PIN attempts

The first line is the correct PIN. After it come the user's attempts, one per line. The user
has **3 attempts**.

- Correct attempt: print `Welcome` and stop. Do **not** read any more lines.
- Wrong attempt with attempts remaining: print `Wrong PIN. 2 tries left` or
  `Wrong PIN. 1 try left`.
- Third wrong attempt: print `Wrong PIN. Card blocked`.

Compare after stripping spaces. A PIN is text, so `0042` and `42` are different.

**Example**

Input:
```
4321
1234
4321
```
Output:
```
Wrong PIN. 2 tries left
Welcome
```

The tests give only as many attempt lines as your program should read. Reading one line
too many crashes with `EOFError`.
