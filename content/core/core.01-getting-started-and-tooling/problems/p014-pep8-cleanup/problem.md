# PEP 8 cleanup

`starter.py` works, but it is hard to read. Rewrite it to follow PEP 8 while
printing exactly the same output:

```
Name: Asha
Age: 19
Subjects: 3
Total: 254
```

The tests check these rules:

1. Every variable name is `snake_case`: only lowercase letters, digits and
   `_`. Names must say what they hold, and never be `l`, `O` or `I`.
2. One statement per line: no `;`.
3. One space on each side of `=` in an assignment, and around `+`.
4. No space before the `(` of a call: `print(x)`, not `print (x)`.
5. No space just inside brackets: `print(x)`, not `print( x )`.
6. One space after every comma.
7. No line longer than 79 characters.

**Example**

`StudentName="Asha"` becomes `student_name = "Asha"`.
