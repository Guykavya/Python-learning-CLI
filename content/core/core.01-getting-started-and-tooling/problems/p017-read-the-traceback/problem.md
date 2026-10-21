# Read the traceback

Here is `report.py`, with line numbers shown on the left (they are not part of
the code):

```python
1  name = "Riya"
2  marks = 87
3  print("Student:", name)
4  print("Marks:", marks)
5  message = "Total: " + marks
6  print(message)
7  print("Done")
```

Do not run it. Predict what happens when you run `python3 report.py`, and
write in `answer.txt`:

1. every line the program prints normally (before any error), in order,
2. then a line `line N`, where N is the line number the traceback reports,
3. then the **last line** of the traceback (error type, colon, message),
   exactly as Python prints it.

**Format example** (for a different program):

```
Hello
line 3
ZeroDivisionError: division by zero
```

Hint for the exact message: it says that it "can only concatenate" one type to
another, and names the type that was wrongly given in brackets.
